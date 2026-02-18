"""Summarization component for generating video summaries and key points."""

import os
import json
import re
from typing import List, Optional

from src.models import Transcript, Summary, KeyPoint
from src.timestamp_formatter import format_timestamp
from src.bedrock_client import BedrockClient, BedrockError


def generate_summary(transcript: Transcript, max_key_points: int = 10, use_ai: bool = True) -> Summary:
    """
    Generate summary from transcript.
    
    Args:
        transcript: Full transcript with timestamps
        max_key_points: Maximum number of key points to extract
        use_ai: Whether to use AI (AWS Bedrock) for summarization
        
    Returns:
        Summary object with overview and key points
    """
    # Check if AI summarization is enabled
    use_ai = use_ai and os.getenv('USE_AI_SUMMARY', 'true').lower() == 'true'
    
    if use_ai:
        try:
            # Use AWS Bedrock for AI-powered summarization
            return _generate_bedrock_summary(transcript, max_key_points)
        except (BedrockError, Exception) as e:
            print(f"Warning: AI summarization failed ({str(e)}), falling back to rule-based approach")
            # Fall back to rule-based approach
    
    # Rule-based summarization (fallback)
    plain_text = transcript.get_plain_text()
    key_points = extract_key_points(transcript, max_key_points)
    overview = _generate_overview(plain_text)
    
    return Summary(
        overview=overview,
        key_points=key_points
    )


def extract_key_points(transcript: Transcript, count: int) -> List[KeyPoint]:
    """
    Extract key points from transcript using AI analysis.
    
    Args:
        transcript: Full transcript with segments
        count: Number of key points to extract
        
    Returns:
        List of key points with timestamps
    """
    # For now, implement a simple version that extracts evenly spaced points
    # In production, this would use an LLM API
    
    if not transcript.segments:
        return []
    
    # Calculate interval for evenly spaced key points
    num_segments = len(transcript.segments)
    interval = max(1, num_segments // count)
    
    key_points = []
    for i in range(0, num_segments, interval):
        if len(key_points) >= count:
            break
        
        segment = transcript.segments[i]
        
        # Format timestamp
        timestamp = format_timestamp(segment.start_time)
        
        # Create more meaningful key point text by combining nearby segments
        # This provides better context than just a single fragment
        key_point_text = _create_meaningful_key_point(transcript.segments, i, context_window=5)
        
        # Create key point
        key_point = KeyPoint(
            text=key_point_text,
            timestamp=timestamp,
            start_time=segment.start_time,
            relevance_score=1.0 - (i / num_segments)  # Simple relevance scoring
        )
        key_points.append(key_point)
    
    return key_points


def _create_meaningful_key_point(segments: List, index: int, context_window: int = 5) -> str:
    """
    Create a meaningful key point by combining nearby segments for context.
    
    Args:
        segments: All transcript segments
        index: Index of the main segment
        context_window: Number of segments to include after for context (default: 5)
        
    Returns:
        Combined text that provides meaningful context
    """
    # Get segments within the context window (current + next few segments)
    start_idx = index
    end_idx = min(len(segments), index + context_window + 1)
    
    # Combine text from segments
    combined_text = ' '.join(seg.text for seg in segments[start_idx:end_idx])
    
    # Clean up the text
    combined_text = combined_text.strip()
    
    # Limit length to avoid overly long key points (around 200-250 characters for more detail)
    max_length = 250
    if len(combined_text) > max_length:
        # Try to cut at a sentence or word boundary
        truncated = combined_text[:max_length]
        last_space = truncated.rfind(' ')
        if last_space > max_length * 0.7:  # Only cut at space if it's not too early
            combined_text = truncated[:last_space] + '...'
        else:
            combined_text = truncated + '...'
    
    return combined_text


def _generate_overview(text: str, max_sentences: int = 3) -> str:
    """
    Generate a brief overview from text.
    
    Args:
        text: Full transcript text
        max_sentences: Maximum number of sentences in overview
        
    Returns:
        Overview string (2-3 sentences)
    """
    # Simple implementation: extract first few sentences
    # In production, this would use an LLM API
    
    if not text:
        return "No content available."
    
    # Split into sentences (simple approach)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Take first max_sentences
    overview_sentences = sentences[:max_sentences]
    overview = '. '.join(overview_sentences)
    
    # Ensure it ends with a period
    if overview and not overview.endswith('.'):
        overview += '.'
    
    return overview if overview else "No content available."


def _generate_bedrock_summary(transcript: Transcript, max_key_points: int = 10) -> Summary:
    """
    Generate AI-powered summary using AWS Bedrock.
    
    Args:
        transcript: Full transcript with timestamps
        max_key_points: Maximum number of key points to extract
        
    Returns:
        Summary object with AI-generated overview and key points
        
    Raises:
        BedrockError: If Bedrock API call fails
    """
    # Initialize Bedrock client
    bedrock = BedrockClient()
    
    # Prepare transcript with timestamps for context
    transcript_with_timestamps = _format_transcript_for_ai(transcript)
    
    # Create prompt
    prompt = _create_ai_prompt(transcript_with_timestamps, max_key_points)
    
    # Call Bedrock
    response_text = bedrock.invoke_model(
        prompt=prompt,
        max_tokens=2048,
        temperature=0.7
    )
    
    # Parse and return summary
    return _parse_ai_response(response_text, max_key_points)


def _create_ai_prompt(transcript_with_timestamps: str, max_key_points: int) -> str:
    """
    Create prompt for AI summarization.
    
    Args:
        transcript_with_timestamps: Formatted transcript
        max_key_points: Number of key points to extract
        
    Returns:
        Prompt string
    """
    return f"""Analyze this video transcript and provide:

1. A brief 2-3 sentence overview summarizing the main topic and key takeaways
2. Extract {max_key_points} key points from the video with their timestamps

Transcript with timestamps:
{transcript_with_timestamps}

Please respond in the following JSON format:
{{
    "overview": "Your 2-3 sentence overview here",
    "key_points": [
        {{"timestamp": "MM:SS", "text": "Key point description"}},
        ...
    ]
}}

Important: 
- Make the overview concise and informative
- Each key point should be a complete, meaningful statement (not fragments)
- Use the exact timestamps from the transcript
- Ensure key points are evenly distributed throughout the video"""


def _parse_ai_response(response_text: str, max_key_points: int) -> Summary:
    """
    Parse AI response and create Summary object.
    
    Args:
        response_text: Raw response from AI
        max_key_points: Maximum number of key points
        
    Returns:
        Summary object
        
    Raises:
        Exception: If parsing fails
    """
    try:
        # Extract JSON from response (handle markdown code blocks if present)
        json_text = response_text.strip()
        if json_text.startswith('```'):
            # Remove markdown code block markers
            lines = json_text.split('\n')
            json_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else json_text
        
        response_data = json.loads(json_text)
        
        # Extract overview
        overview = response_data.get('overview', 'No overview available.')
        
        # Extract and format key points
        key_points = []
        for kp_data in response_data.get('key_points', [])[:max_key_points]:
            timestamp = kp_data.get('timestamp', '00:00')
            text = kp_data.get('text', '')
            
            # Find the closest segment to get accurate start_time
            start_time = _parse_timestamp_to_seconds(timestamp)
            
            key_point = KeyPoint(
                text=text,
                timestamp=timestamp,
                start_time=start_time,
                relevance_score=1.0
            )
            key_points.append(key_point)
        
        return Summary(
            overview=overview,
            key_points=key_points
        )
        
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse AI response as JSON: {str(e)}")


def _format_transcript_for_ai(transcript: Transcript, max_length: int = 8000) -> str:
    """
    Format transcript with timestamps for AI processing.
    
    Args:
        transcript: Transcript object
        max_length: Maximum character length (to avoid token limits)
        
    Returns:
        Formatted transcript string with timestamps
    """
    formatted_lines = []
    total_length = 0
    
    for segment in transcript.segments:
        timestamp = format_timestamp(segment.start_time)
        line = f"[{timestamp}] {segment.text}"
        
        if total_length + len(line) > max_length:
            formatted_lines.append("... (transcript truncated due to length)")
            break
        
        formatted_lines.append(line)
        total_length += len(line)
    
    return '\n'.join(formatted_lines)


def _parse_timestamp_to_seconds(timestamp: str) -> float:
    """
    Parse timestamp string (MM:SS or HH:MM:SS) to seconds.
    
    Args:
        timestamp: Timestamp string
        
    Returns:
        Time in seconds
    """
    try:
        parts = timestamp.split(':')
        if len(parts) == 2:
            # MM:SS format
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        elif len(parts) == 3:
            # HH:MM:SS format
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        else:
            return 0.0
    except (ValueError, AttributeError):
        return 0.0


