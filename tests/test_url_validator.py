"""Tests for URL validation."""

from hypothesis import given, strategies as st
import pytest

from src.url_validator import extract_video_id, validate_youtube_url
from src.models import Ok, Err, ErrorType


# Custom strategy for valid YouTube video IDs (11 characters, alphanumeric + - and _)
@st.composite
def video_ids(draw):
    """Generate valid YouTube video IDs."""
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'
    return ''.join(draw(st.sampled_from(chars)) for _ in range(11))


@st.composite
def youtube_urls(draw):
    """Generate valid YouTube URLs in various formats."""
    video_id = draw(video_ids())
    format_choice = draw(st.integers(min_value=0, max_value=2))
    
    if format_choice == 0:
        return f"https://www.youtube.com/watch?v={video_id}"
    elif format_choice == 1:
        return f"https://youtu.be/{video_id}"
    else:
        # With additional query parameters
        return f"https://www.youtube.com/watch?v={video_id}&t=10s"


class TestURLValidation:
    """Tests for URL validation component."""
    
    # Feature: youtube-transcript-summarizer, Property 1: Valid YouTube URLs are accepted
    @given(youtube_urls())
    def test_valid_youtube_urls_are_accepted(self, url: str):
        """
        Property 1: Valid YouTube URLs are accepted.
        
        For any valid YouTube URL (in youtube.com/watch?v= or youtu.be/ format),
        the validator should successfully validate it and return success.
        
        **Validates: Requirements 1.1, 1.4**
        """
        result = validate_youtube_url(url)
        assert isinstance(result, Ok), f"Expected Ok, got Err: {result.error if isinstance(result, Err) else None}"
        assert result.value.video_id is not None
        assert len(result.value.video_id) > 0
        assert result.value.original_url == url


class TestVideoIDExtraction:
    """Tests for video ID extraction."""
    
    # Feature: youtube-transcript-summarizer, Property 2: Video ID extraction consistency
    @given(video_ids())
    def test_video_id_extraction_consistency(self, video_id: str):
        """
        Property 2: Video ID extraction consistency.
        
        For any valid YouTube URL, extracting the video ID should produce
        the same ID regardless of URL format (youtube.com vs youtu.be).
        
        **Validates: Requirements 1.2**
        """
        url1 = f"https://www.youtube.com/watch?v={video_id}"
        url2 = f"https://youtu.be/{video_id}"
        
        extracted_id1 = extract_video_id(url1)
        extracted_id2 = extract_video_id(url2)
        
        assert extracted_id1 == video_id
        assert extracted_id2 == video_id
        assert extracted_id1 == extracted_id2


class TestInvalidURLRejection:
    """Tests for invalid URL rejection."""
    
    # Feature: youtube-transcript-summarizer, Property 3: Invalid URLs are rejected with errors
    @given(st.one_of(
        st.text().filter(lambda x: 'youtube.com' not in x and 'youtu.be' not in x),
        st.just(""),
        st.just("https://example.com"),
        st.just("https://www.youtube.com/"),
        st.just("https://www.youtube.com/watch"),
    ))
    def test_invalid_urls_are_rejected(self, url: str):
        """
        Property 3: Invalid URLs are rejected with errors.
        
        For any invalid URL string, the validator should reject it
        and return a descriptive error message.
        
        **Validates: Requirements 1.3**
        """
        result = validate_youtube_url(url)
        assert isinstance(result, Err), f"Expected Err for invalid URL: {url}"
        assert result.error.error_type == ErrorType.INVALID_URL
        assert len(result.error.message) > 0


class TestURLValidationUnitTests:
    """Unit tests for URL validation with specific examples."""
    
    def test_youtube_com_watch_format(self):
        """Test standard youtube.com/watch?v= format."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = validate_youtube_url(url)
        
        assert isinstance(result, Ok)
        assert result.value.video_id == "dQw4w9WgXcQ"
        assert result.value.original_url == url
    
    def test_youtu_be_format(self):
        """Test short youtu.be format."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        result = validate_youtube_url(url)
        
        assert isinstance(result, Ok)
        assert result.value.video_id == "dQw4w9WgXcQ"
        assert result.value.original_url == url
    
    def test_youtube_url_with_query_params(self):
        """Test URL with additional query parameters."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s&list=PLtest"
        result = validate_youtube_url(url)
        
        assert isinstance(result, Ok)
        assert result.value.video_id == "dQw4w9WgXcQ"
    
    def test_empty_string(self):
        """Test empty string is rejected."""
        result = validate_youtube_url("")
        
        assert isinstance(result, Err)
        assert result.error.error_type == ErrorType.INVALID_URL
    
    def test_non_youtube_url(self):
        """Test non-YouTube URL is rejected."""
        result = validate_youtube_url("https://example.com/video")
        
        assert isinstance(result, Err)
        assert result.error.error_type == ErrorType.INVALID_URL
    
    def test_malformed_youtube_url(self):
        """Test malformed YouTube URL is rejected."""
        result = validate_youtube_url("https://www.youtube.com/")
        
        assert isinstance(result, Err)
        assert result.error.error_type == ErrorType.INVALID_URL
    
    def test_youtube_watch_without_video_id(self):
        """Test youtube.com/watch without v parameter."""
        result = validate_youtube_url("https://www.youtube.com/watch")
        
        assert isinstance(result, Err)
        assert result.error.error_type == ErrorType.INVALID_URL
    
    def test_extract_video_id_youtube_com(self):
        """Test extracting video ID from youtube.com format."""
        video_id = extract_video_id("https://www.youtube.com/watch?v=abc123XYZ-_")
        assert video_id == "abc123XYZ-_"
    
    def test_extract_video_id_youtu_be(self):
        """Test extracting video ID from youtu.be format."""
        video_id = extract_video_id("https://youtu.be/abc123XYZ-_")
        assert video_id == "abc123XYZ-_"
    
    def test_extract_video_id_returns_none_for_invalid(self):
        """Test extract_video_id returns None for invalid URLs."""
        assert extract_video_id("") is None
        assert extract_video_id("https://example.com") is None
        assert extract_video_id("not a url") is None
