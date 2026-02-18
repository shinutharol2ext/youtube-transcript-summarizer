"""Tests for transcript fetching."""

from hypothesis import given, strategies as st
from unittest.mock import patch, MagicMock
import pytest

from src.transcript_fetcher import fetch_transcript, get_plain_text
from src.models import Transcript, TranscriptSegment, Ok, Err, ErrorType


# Custom strategy for transcript segments
@st.composite
def transcript_segments(draw, min_segments=1, max_segments=10):
    """Generate a list of transcript segments."""
    num_segments = draw(st.integers(min_value=min_segments, max_value=max_segments))
    segments = []
    current_time = 0.0
    
    for _ in range(num_segments):
        text = draw(st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',))))
        duration = draw(st.floats(min_value=0.1, max_value=10.0))
        
        segment = TranscriptSegment(
            text=text,
            start_time=current_time,
            duration=duration
        )
        segments.append(segment)
        current_time += duration
    
    return segments


class TestPlainTextOrdering:
    """Tests for plain text ordering."""
    
    # Feature: youtube-transcript-summarizer, Property 4: Plain text preserves chronological order
    @given(transcript_segments())
    def test_plain_text_preserves_chronological_order(self, segments):
        """
        Property 4: Plain text preserves chronological order.
        
        For any list of transcript segments, converting to plain text
        should preserve the chronological order of segments based on start_time.
        
        **Validates: Requirements 2.2**
        """
        # Create transcript with segments
        transcript = Transcript(
            segments=segments,
            language="en",
            video_id="test_video"
        )
        
        # Get plain text
        plain_text = get_plain_text(transcript)
        
        # Verify order is preserved
        expected_text = " ".join(seg.text for seg in segments)
        assert plain_text == expected_text
        
        # Verify all segment texts appear in order
        for segment in segments:
            assert segment.text in plain_text


class TestTranscriptFetchingUnitTests:
    """Unit tests for transcript fetching with mocked API."""
    
    @patch('src.transcript_fetcher.YouTubeTranscriptApi')
    def test_successful_transcript_retrieval(self, mock_api_class):
        """Test successful transcript retrieval."""
        # Create mock FetchedTranscript object
        from collections import namedtuple
        Snippet = namedtuple('Snippet', ['text', 'start', 'duration'])
        FetchedTranscript = namedtuple('FetchedTranscript', ['snippets', 'video_id', 'language'])
        
        mock_fetched = FetchedTranscript(
            snippets=[
                Snippet(text='Hello world', start=0.0, duration=2.0),
                Snippet(text='This is a test', start=2.0, duration=3.0),
            ],
            video_id='test_video_id',
            language='en'
        )
        
        mock_api_instance = mock_api_class.return_value
        mock_api_instance.fetch.return_value = mock_fetched
        
        result = fetch_transcript("test_video_id")
        
        assert isinstance(result, Ok)
        assert len(result.value.segments) == 2
        assert result.value.segments[0].text == 'Hello world'
        assert result.value.segments[1].text == 'This is a test'
        assert result.value.video_id == "test_video_id"
        assert result.value.language == "en"
    
    @patch('src.transcript_fetcher.YouTubeTranscriptApi')
    def test_video_not_found_error(self, mock_api_class):
        """Test VIDEO_NOT_FOUND error for missing videos."""
        from youtube_transcript_api._errors import VideoUnavailable
        
        mock_api_instance = mock_api_class.return_value
        mock_api_instance.fetch.side_effect = VideoUnavailable("test_video_id")
        
        result = fetch_transcript("test_video_id")
        
        assert isinstance(result, Err)
        assert result.error.error_type == ErrorType.VIDEO_NOT_FOUND
        assert "not found" in result.error.message.lower() or "private" in result.error.message.lower()
    
    @patch('src.transcript_fetcher.YouTubeTranscriptApi')
    def test_transcript_not_available_error(self, mock_api_class):
        """Test TRANSCRIPT_NOT_AVAILABLE when no transcript exists."""
        from youtube_transcript_api._errors import TranscriptsDisabled
        
        mock_api_instance = mock_api_class.return_value
        mock_api_instance.fetch.side_effect = TranscriptsDisabled("test_video_id")
        
        result = fetch_transcript("test_video_id")
        
        assert isinstance(result, Err)
        assert result.error.error_type == ErrorType.TRANSCRIPT_NOT_AVAILABLE
        assert "no transcript" in result.error.message.lower()
    
    @patch('src.transcript_fetcher.YouTubeTranscriptApi')
    def test_language_not_available_error(self, mock_api_class):
        """Test LANGUAGE_NOT_AVAILABLE when English not available."""
        from youtube_transcript_api._errors import NoTranscriptFound
        
        mock_api_instance = mock_api_class.return_value
        mock_api_instance.fetch.side_effect = NoTranscriptFound(
            "test_video_id",
            ["en"],
            []
        )
        
        result = fetch_transcript("test_video_id")
        
        assert isinstance(result, Err)
        assert result.error.error_type == ErrorType.LANGUAGE_NOT_AVAILABLE
        assert "transcript not available" in result.error.message.lower()
    
    @patch('src.transcript_fetcher.YouTubeTranscriptApi')
    def test_network_error_handling(self, mock_api_class):
        """Test network error handling."""
        mock_api_instance = mock_api_class.return_value
        mock_api_instance.fetch.side_effect = ConnectionError("Network timeout")
        
        result = fetch_transcript("test_video_id")
        
        assert isinstance(result, Err)
        assert result.error.error_type == ErrorType.NETWORK_ERROR
        assert "network error" in result.error.message.lower()
    
    def test_get_plain_text_concatenates_segments(self):
        """Test get_plain_text concatenates all segments."""
        segments = [
            TranscriptSegment(text="First segment", start_time=0.0, duration=2.0),
            TranscriptSegment(text="Second segment", start_time=2.0, duration=3.0),
            TranscriptSegment(text="Third segment", start_time=5.0, duration=2.5),
        ]
        
        transcript = Transcript(
            segments=segments,
            language="en",
            video_id="test"
        )
        
        plain_text = get_plain_text(transcript)
        
        assert plain_text == "First segment Second segment Third segment"
    
    def test_get_plain_text_empty_transcript(self):
        """Test get_plain_text with empty transcript."""
        transcript = Transcript(
            segments=[],
            language="en",
            video_id="test"
        )
        
        plain_text = get_plain_text(transcript)
        
        assert plain_text == ""
