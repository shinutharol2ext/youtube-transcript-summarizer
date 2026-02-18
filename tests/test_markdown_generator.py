"""Tests for markdown generation."""

from hypothesis import given, strategies as st
import pytest
import re

from src.markdown_generator import (
    generate_markdown,
    format_transcript_section,
    format_summary_section
)
from src.models import Transcript, TranscriptSegment, Summary, KeyPoint


# Custom strategies
@st.composite
def transcript_segments(draw, min_segments=3, max_segments=10):
    """Generate transcript segments."""
    num_segments = draw(st.integers(min_value=min_segments, max_value=max_segments))
    segments = []
    current_time = 0.0
    
    for _ in range(num_segments):
        text = draw(st.text(min_size=5, max_size=50, alphabet=st.characters(
            blacklist_categories=('Cs',),
            blacklist_characters='\n\r\t#*'
        )))
        duration = draw(st.floats(min_value=1.0, max_value=5.0))
        
        segment = TranscriptSegment(
            text=text,
            start_time=current_time,
            duration=duration
        )
        segments.append(segment)
        current_time += duration
    
    return segments


@st.composite
def key_points(draw, min_points=2, max_points=5):
    """Generate key points."""
    num_points = draw(st.integers(min_value=min_points, max_value=max_points))
    points = []
    
    for i in range(num_points):
        text = draw(st.text(min_size=5, max_size=50, alphabet=st.characters(
            blacklist_categories=('Cs',),
            blacklist_characters='\n\r\t#*'
        )))
        timestamp = f"{i:02d}:{i*10:02d}"
        
        point = KeyPoint(
            text=text,
            timestamp=timestamp,
            start_time=float(i * 60),
            relevance_score=0.9
        )
        points.append(point)
    
    return points


class TestMarkdownSections:
    """Tests for markdown section generation."""
    
    # Feature: youtube-transcript-summarizer, Property 7: Markdown contains all required sections
    @given(transcript_segments(), key_points(), st.text(min_size=5, max_size=50))
    def test_markdown_contains_all_required_sections(self, segments, kp_list, video_title):
        """
        Property 7: Markdown contains all required sections.
        
        For any generated markdown document, it should contain sections
        for transcript, overview summary, and key points with timestamps.
        
        **Validates: Requirements 4.2, 4.3, 4.4**
        """
        transcript = Transcript(
            segments=segments,
            language="en",
            video_id="test"
        )
        
        summary = Summary(
            overview="This is a test overview.",
            key_points=kp_list
        )
        
        markdown_doc = generate_markdown(transcript, summary, video_title)
        content = markdown_doc.content
        
        # Check for required sections
        assert "## Overview" in content, "Missing Overview section"
        assert "## Key Points" in content, "Missing Key Points section"
        assert "## Full Transcript" in content, "Missing Full Transcript section"
        
        # Check that overview text is present
        assert "This is a test overview." in content
        
        # Check that key points are present with timestamps
        for kp in kp_list:
            assert kp.timestamp in content, f"Missing timestamp {kp.timestamp}"


class TestMarkdownValidity:
    """Tests for markdown syntax validity."""
    
    # Feature: youtube-transcript-summarizer, Property 8: Markdown is syntactically valid
    @given(transcript_segments(), key_points(), st.text(min_size=1, max_size=50))
    def test_markdown_is_syntactically_valid(self, segments, kp_list, video_title):
        """
        Property 8: Markdown is syntactically valid.
        
        For any generated markdown document, it should be valid markdown
        with proper headers, lists, and formatting.
        
        **Validates: Requirements 4.5**
        """
        transcript = Transcript(
            segments=segments,
            language="en",
            video_id="test"
        )
        
        summary = Summary(
            overview="Test overview",
            key_points=kp_list
        )
        
        markdown_doc = generate_markdown(transcript, summary, video_title)
        content = markdown_doc.content
        
        # Check for valid markdown headers
        assert re.search(r'^# .+', content, re.MULTILINE), "Missing level 1 header"
        assert re.search(r'^## .+', content, re.MULTILINE), "Missing level 2 headers"
        
        # Check for valid list items (key points)
        assert re.search(r'^- \*\*.+\*\* - .+', content, re.MULTILINE), "Missing valid list items"


class TestMarkdownGenerationUnitTests:
    """Unit tests for markdown generation."""
    
    def test_format_transcript_section(self):
        """Test transcript section formatting."""
        segments = [
            TranscriptSegment(text="First segment", start_time=0.0, duration=2.0),
            TranscriptSegment(text="Second segment", start_time=2.0, duration=3.0),
        ]
        
        transcript = Transcript(
            segments=segments,
            language="en",
            video_id="test"
        )
        
        section = format_transcript_section(transcript)
        
        assert "## Full Transcript" in section
        assert "First segment Second segment" in section
    
    def test_format_summary_section(self):
        """Test summary section formatting."""
        key_points = [
            KeyPoint(text="Point 1", timestamp="00:10", start_time=10.0, relevance_score=0.9),
            KeyPoint(text="Point 2", timestamp="00:30", start_time=30.0, relevance_score=0.8),
        ]
        
        summary = Summary(
            overview="This is an overview.",
            key_points=key_points
        )
        
        section = format_summary_section(summary)
        
        assert "## Overview" in section
        assert "This is an overview." in section
        assert "## Key Points" in section
        assert "**00:10** - Point 1" in section
        assert "**00:30** - Point 2" in section
    
    def test_generate_markdown_complete_document(self):
        """Test complete markdown document generation."""
        segments = [
            TranscriptSegment(text="Hello world", start_time=0.0, duration=2.0),
        ]
        
        transcript = Transcript(
            segments=segments,
            language="en",
            video_id="test"
        )
        
        key_points = [
            KeyPoint(text="Introduction", timestamp="00:00", start_time=0.0, relevance_score=1.0),
        ]
        
        summary = Summary(
            overview="A simple test video.",
            key_points=key_points
        )
        
        markdown_doc = generate_markdown(transcript, summary, "Test Video")
        
        assert markdown_doc.video_title == "Test Video"
        assert "# Test Video" in markdown_doc.content
        assert "## Overview" in markdown_doc.content
        assert "## Key Points" in markdown_doc.content
        assert "## Full Transcript" in markdown_doc.content
    
    def test_markdown_structure_order(self):
        """Test that markdown sections appear in correct order."""
        segments = [
            TranscriptSegment(text="Content", start_time=0.0, duration=1.0),
        ]
        
        transcript = Transcript(
            segments=segments,
            language="en",
            video_id="test"
        )
        
        summary = Summary(
            overview="Overview text",
            key_points=[]
        )
        
        markdown_doc = generate_markdown(transcript, summary, "Title")
        content = markdown_doc.content
        
        # Find positions of sections
        title_pos = content.find("# Title")
        overview_pos = content.find("## Overview")
        key_points_pos = content.find("## Key Points")
        transcript_pos = content.find("## Full Transcript")
        
        # Verify order
        assert title_pos < overview_pos
        assert overview_pos < key_points_pos
        assert key_points_pos < transcript_pos
