"""Tests for summarization component."""

from hypothesis import given, strategies as st
import pytest
import re

from src.summarizer import generate_summary, extract_key_points
from src.models import Transcript, TranscriptSegment


# Custom strategy for transcript segments
@st.composite
def transcript_segments(draw, min_segments=5, max_segments=20):
    """Generate a list of transcript segments."""
    num_segments = draw(st.integers(min_value=min_segments, max_value=max_segments))
    segments = []
    current_time = 0.0
    
    for _ in range(num_segments):
        text = draw(st.text(min_size=10, max_size=100, alphabet=st.characters(
            blacklist_categories=('Cs',),
            blacklist_characters='\n\r\t'
        )))
        duration = draw(st.floats(min_value=1.0, max_value=10.0))
        
        segment = TranscriptSegment(
            text=text,
            start_time=current_time,
            duration=duration
        )
        segments.append(segment)
        current_time += duration
    
    return segments


class TestKeyPointTimestamps:
    """Tests for key point timestamp validation."""
    
    # Feature: youtube-transcript-summarizer, Property 5: All key points have timestamps
    @given(transcript_segments())
    def test_all_key_points_have_timestamps(self, segments):
        """
        Property 5: All key points have timestamps.
        
        For any generated summary, every key point should have
        an associated timestamp in the correct format.
        
        **Validates: Requirements 3.3**
        """
        transcript = Transcript(
            segments=segments,
            language="en",
            video_id="test_video"
        )
        
        summary = generate_summary(transcript, max_key_points=5)
        
        # Verify all key points have timestamps
        for key_point in summary.key_points:
            assert key_point.timestamp is not None
            assert len(key_point.timestamp) > 0
            
            # Verify timestamp format (MM:SS or HH:MM:SS)
            assert re.match(r'^\d{2}:\d{2}(:\d{2})?$', key_point.timestamp), \
                f"Invalid timestamp format: {key_point.timestamp}"
            
            # Verify start_time is set
            assert key_point.start_time >= 0


class TestSummarizationUnitTests:
    """Unit tests for summarization with specific examples."""
    
    def test_generate_summary_with_sample_transcript(self):
        """Test summary generation with sample transcript."""
        segments = [
            TranscriptSegment(text="Welcome to this tutorial", start_time=0.0, duration=2.0),
            TranscriptSegment(text="Today we will learn about Python", start_time=2.0, duration=3.0),
            TranscriptSegment(text="Python is a programming language", start_time=5.0, duration=3.0),
            TranscriptSegment(text="It is easy to learn", start_time=8.0, duration=2.0),
            TranscriptSegment(text="Let's get started", start_time=10.0, duration=2.0),
        ]
        
        transcript = Transcript(
            segments=segments,
            language="en",
            video_id="test"
        )
        
        summary = generate_summary(transcript, max_key_points=3)
        
        assert summary.overview is not None
        assert len(summary.overview) > 0
        assert len(summary.key_points) <= 3
        assert len(summary.key_points) > 0
    
    def test_extract_key_points_returns_correct_count(self):
        """Test that extract_key_points returns requested number of points."""
        segments = [
            TranscriptSegment(text=f"Segment {i}", start_time=float(i), duration=1.0)
            for i in range(20)
        ]
        
        transcript = Transcript(
            segments=segments,
            language="en",
            video_id="test"
        )
        
        key_points = extract_key_points(transcript, count=5)
        
        assert len(key_points) == 5
    
    def test_extract_key_points_with_empty_transcript(self):
        """Test extract_key_points with empty transcript."""
        transcript = Transcript(
            segments=[],
            language="en",
            video_id="test"
        )
        
        key_points = extract_key_points(transcript, count=5)
        
        assert len(key_points) == 0
    
    def test_key_points_have_timestamps(self):
        """Test that all key points have properly formatted timestamps."""
        segments = [
            TranscriptSegment(text="First point", start_time=0.0, duration=2.0),
            TranscriptSegment(text="Second point", start_time=2.0, duration=3.0),
            TranscriptSegment(text="Third point", start_time=5.0, duration=2.0),
        ]
        
        transcript = Transcript(
            segments=segments,
            language="en",
            video_id="test"
        )
        
        key_points = extract_key_points(transcript, count=3)
        
        for kp in key_points:
            assert kp.timestamp is not None
            assert re.match(r'^\d{2}:\d{2}(:\d{2})?$', kp.timestamp)
            assert kp.start_time >= 0
    
    def test_summary_overview_is_not_empty(self):
        """Test that summary overview is generated."""
        segments = [
            TranscriptSegment(text="This is a test video", start_time=0.0, duration=2.0),
            TranscriptSegment(text="It covers important topics", start_time=2.0, duration=3.0),
        ]
        
        transcript = Transcript(
            segments=segments,
            language="en",
            video_id="test"
        )
        
        summary = generate_summary(transcript)
        
        assert summary.overview is not None
        assert len(summary.overview) > 0
    
    def test_key_points_have_relevance_scores(self):
        """Test that key points have relevance scores."""
        segments = [
            TranscriptSegment(text=f"Point {i}", start_time=float(i), duration=1.0)
            for i in range(10)
        ]
        
        transcript = Transcript(
            segments=segments,
            language="en",
            video_id="test"
        )
        
        key_points = extract_key_points(transcript, count=5)
        
        for kp in key_points:
            assert 0.0 <= kp.relevance_score <= 1.0
