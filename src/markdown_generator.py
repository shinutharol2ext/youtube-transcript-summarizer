"""Markdown generation for video transcripts and summaries."""

from src.models import Transcript, Summary, MarkdownDocument
from src.transcript_fetcher import get_plain_text


def generate_markdown(transcript: Transcript, summary: Summary, video_title: str) -> MarkdownDocument:
    """
    Generate formatted markdown document.
    
    Args:
        transcript: Full transcript data
        summary: Summary with overview and key points
        video_title: Title of the video
        
    Returns:
        MarkdownDocument with formatted content
    """
    # Sanitize title - remove newlines and ensure it's not empty
    sanitized_title = video_title.strip().replace('\n', ' ').replace('\r', ' ')
    if not sanitized_title:
        sanitized_title = "Untitled Video"
    
    # Build markdown sections
    title_section = f"# {sanitized_title}\n\n"
    summary_section = format_summary_section(summary)
    detailed_summary_section = format_detailed_summary_section(summary)
    transcript_section = format_transcript_section(transcript)
    
    # Combine all sections: Title → Overview → Key Points → Summary → Full Transcript
    content = title_section + summary_section + "\n" + detailed_summary_section + "\n" + transcript_section
    
    return MarkdownDocument(
        content=content,
        video_title=sanitized_title
    )


def format_transcript_section(transcript: Transcript) -> str:
    """
    Format transcript as markdown section.
    
    Args:
        transcript: Transcript data
        
    Returns:
        Markdown-formatted transcript section
    """
    plain_text = get_plain_text(transcript)
    
    section = "## Full Transcript\n\n"
    section += plain_text
    section += "\n"
    
    return section


def format_summary_section(summary: Summary) -> str:
    """
    Format summary as markdown section.
    
    Args:
        summary: Summary with overview and key points
        
    Returns:
        Markdown-formatted summary section
    """
    # Overview section
    section = "## Overview\n\n"
    section += summary.overview
    section += "\n\n"
    
    # Key points section
    section += "## Key Points\n\n"
    
    for key_point in summary.key_points:
        section += f"- **{key_point.timestamp}** - {key_point.text}\n"
    
    section += "\n"
    
    return section


def format_detailed_summary_section(summary: Summary) -> str:
    """
    Format detailed summary section with just the overview.
    
    The Summary section now provides a concise, meaningful overview without
    repeating the key points that are already listed in the Key Points section.
    
    Args:
        summary: Summary with overview and key points
        
    Returns:
        Markdown-formatted detailed summary section
    """
    section = "## Summary\n\n"
    
    # Just add the overview - it provides the meaningful summary
    # Key points are already listed in their own section above
    section += summary.overview
    section += "\n\n"
    
    return section
