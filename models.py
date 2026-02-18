"""Data models for YouTube Transcript Summarizer."""

from dataclasses import dataclass
from typing import List, Optional, Generic, TypeVar, Union
from enum import Enum


# Result type for error handling
T = TypeVar('T')
E = TypeVar('E')


@dataclass
class Ok(Generic[T]):
    """Success result containing a value."""
    value: T


@dataclass
class Err(Generic[E]):
    """Error result containing an error."""
    error: E


Result = Union[Ok[T], Err[E]]


# Core data models
@dataclass
class TranscriptSegment:
    """Individual segment of transcript with timing."""
    text: str
    start_time: float  # seconds from video start
    duration: float    # segment duration in seconds


@dataclass
class Transcript:
    """Complete transcript with metadata."""
    segments: List[TranscriptSegment]
    language: str
    video_id: str
    
    def get_plain_text(self) -> str:
        """Concatenate all segments into plain text."""
        return " ".join(seg.text for seg in self.segments)
    
    def get_duration(self) -> float:
        """Calculate total video duration."""
        if not self.segments:
            return 0.0
        last_seg = self.segments[-1]
        return last_seg.start_time + last_seg.duration


@dataclass
class KeyPoint:
    """Key point extracted from video with timestamp."""
    text: str
    timestamp: str  # formatted as MM:SS or HH:MM:SS
    start_time: float  # original time in seconds
    relevance_score: float  # 0.0 to 1.0


@dataclass
class Summary:
    """Summary of video content."""
    overview: str  # 2-3 sentence overview
    key_points: List[KeyPoint]


@dataclass
class YouTubeURL:
    """Parsed YouTube URL."""
    video_id: str
    original_url: str


@dataclass
class MarkdownDocument:
    """Generated markdown content."""
    content: str
    video_title: str


class ErrorType(Enum):
    """Types of errors that can occur."""
    INVALID_URL = "invalid_url"
    VIDEO_NOT_FOUND = "video_not_found"
    TRANSCRIPT_NOT_AVAILABLE = "transcript_not_available"
    LANGUAGE_NOT_AVAILABLE = "language_not_available"
    NETWORK_ERROR = "network_error"
    FILE_WRITE_ERROR = "file_write_error"
    API_RATE_LIMIT = "api_rate_limit"


@dataclass
class ProcessingError:
    """Error information."""
    error_type: ErrorType
    message: str
    details: Optional[str] = None
