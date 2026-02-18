# Design Document: YouTube Transcript Summarizer

## Overview

The YouTube Transcript Summarizer is a command-line agent that processes YouTube videos by URL to generate comprehensive markdown documents containing plain text transcripts and structured summaries. The system leverages YouTube's transcript API to retrieve video captions, then uses AI-powered summarization to extract key points with timestamps.

The agent follows a pipeline architecture: URL validation → transcript retrieval → content analysis → summary generation → markdown formatting → file output. This design ensures separation of concerns and makes each component independently testable.

## Architecture

The system consists of five main components organized in a pipeline:

```
┌─────────────────┐
│  CLI Interface  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  URL Validator  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Transcript Fetcher│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Summarizer    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Markdown Generator│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  File Writer    │
└─────────────────┘
```

**Component Responsibilities:**

1. **CLI Interface**: Entry point, handles user input and orchestrates the pipeline
2. **URL Validator**: Validates and parses YouTube URLs, extracts video IDs
3. **Transcript Fetcher**: Retrieves transcript data from YouTube
4. **Summarizer**: Analyzes transcript content to generate overview and key points
5. **Markdown Generator**: Formats output into structured markdown
6. **File Writer**: Saves markdown content to disk with proper naming

## Components and Interfaces

### CLI Interface

**Purpose**: Provides command-line interface for user interaction

**Interface**:
```python
def main(args: List[str]) -> int:
    """
    Main entry point for the CLI
    
    Args:
        args: Command line arguments including YouTube URL
        
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    pass

def parse_arguments(args: List[str]) -> Arguments:
    """
    Parse command line arguments
    
    Args:
        args: Raw command line arguments
        
    Returns:
        Parsed arguments object
        
    Raises:
        ArgumentError: If arguments are invalid
    """
    pass
```

**Responsibilities**:
- Parse command-line arguments
- Validate required inputs are provided
- Orchestrate the processing pipeline
- Handle top-level error reporting
- Return appropriate exit codes

### URL Validator

**Purpose**: Validates YouTube URLs and extracts video identifiers

**Interface**:
```python
class YouTubeURL:
    video_id: str
    original_url: str

def validate_youtube_url(url: str) -> Result[YouTubeURL, ValidationError]:
    """
    Validate and parse a YouTube URL
    
    Args:
        url: Raw URL string from user input
        
    Returns:
        Result containing YouTubeURL on success or ValidationError on failure
    """
    pass

def extract_video_id(url: str) -> Optional[str]:
    """
    Extract video ID from various YouTube URL formats
    
    Supports:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/watch?v=VIDEO_ID&other=params
    
    Args:
        url: YouTube URL string
        
    Returns:
        Video ID if found, None otherwise
    """
    pass
```

**Responsibilities**:
- Validate URL format
- Support multiple YouTube URL formats (youtube.com/watch, youtu.be)
- Extract video ID from URL
- Return structured error messages for invalid URLs

### Transcript Fetcher

**Purpose**: Retrieves transcript data from YouTube videos

**Interface**:
```python
class TranscriptSegment:
    text: str
    start_time: float  # seconds
    duration: float    # seconds

class Transcript:
    segments: List[TranscriptSegment]
    language: str
    video_id: str

def fetch_transcript(video_id: str, language: str = "en") -> Result[Transcript, FetchError]:
    """
    Fetch transcript for a YouTube video
    
    Args:
        video_id: YouTube video identifier
        language: Language code (default: "en")
        
    Returns:
        Result containing Transcript on success or FetchError on failure
        
    Errors:
        - TranscriptNotAvailable: Video has no transcript
        - VideoNotFound: Video does not exist or is private
        - LanguageNotAvailable: Requested language not available
        - NetworkError: Connection issues
    """
    pass

def get_plain_text(transcript: Transcript) -> str:
    """
    Convert transcript segments to plain text
    
    Args:
        transcript: Transcript object with segments
        
    Returns:
        Plain text string with all spoken content
    """
    pass
```

**Responsibilities**:
- Interface with YouTube transcript API (using youtube-transcript-api library)
- Handle transcript retrieval errors
- Filter for English language transcripts
- Convert segmented transcript to plain text
- Preserve timestamp information for each segment

### Summarizer

**Purpose**: Analyzes transcript content to generate summaries and extract key points

**Interface**:
```python
class KeyPoint:
    text: str
    timestamp: str  # formatted as MM:SS or HH:MM:SS
    relevance_score: float

class Summary:
    overview: str
    key_points: List[KeyPoint]

def generate_summary(transcript: Transcript, max_key_points: int = 10) -> Summary:
    """
    Generate summary from transcript
    
    Args:
        transcript: Full transcript with timestamps
        max_key_points: Maximum number of key points to extract
        
    Returns:
        Summary object with overview and key points
    """
    pass

def format_timestamp(seconds: float) -> str:
    """
    Format seconds into MM:SS or HH:MM:SS
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted timestamp string
    """
    pass

def extract_key_points(transcript: Transcript, count: int) -> List[KeyPoint]:
    """
    Extract key points from transcript using AI analysis
    
    Args:
        transcript: Full transcript with segments
        count: Number of key points to extract
        
    Returns:
        List of key points with timestamps
    """
    pass
```

**Responsibilities**:
- Generate brief overview summary (2-3 sentences)
- Extract key points from content using AI/LLM
- Associate timestamps with key points
- Format timestamps appropriately based on video length
- Rank key points by relevance

**Implementation Note**: This component will use an LLM API (e.g., OpenAI, Anthropic) to analyze the transcript and extract meaningful summaries and key points.

### Markdown Generator

**Purpose**: Formats transcript and summary data into structured markdown

**Interface**:
```python
class MarkdownDocument:
    content: str
    
def generate_markdown(transcript: Transcript, summary: Summary, video_title: str) -> MarkdownDocument:
    """
    Generate formatted markdown document
    
    Args:
        transcript: Full transcript data
        summary: Summary with overview and key points
        video_title: Title of the video
        
    Returns:
        MarkdownDocument with formatted content
    """
    pass

def format_transcript_section(transcript: Transcript) -> str:
    """
    Format transcript as markdown section
    
    Args:
        transcript: Transcript data
        
    Returns:
        Markdown-formatted transcript section
    """
    pass

def format_summary_section(summary: Summary) -> str:
    """
    Format summary as markdown section
    
    Args:
        summary: Summary with overview and key points
        
    Returns:
        Markdown-formatted summary section
    """
    pass
```

**Responsibilities**:
- Create structured markdown with clear sections
- Format transcript section with proper headers
- Format summary section with overview and key points list
- Include timestamps as clickable links (if possible)
- Ensure proper markdown syntax

**Output Structure**:
```markdown
# [Video Title]

## Overview
[Brief 2-3 sentence summary]

## Key Points
- **[MM:SS]** - [Key point 1]
- **[MM:SS]** - [Key point 2]
...

## Full Transcript
[Complete plain text transcript]
```

### File Writer

**Purpose**: Saves markdown content to disk with appropriate naming

**Interface**:
```python
def save_markdown(document: MarkdownDocument, video_title: str, output_dir: str = ".") -> Result[Path, IOError]:
    """
    Save markdown document to file
    
    Args:
        document: Markdown content to save
        video_title: Video title for filename generation
        output_dir: Directory to save file (default: current directory)
        
    Returns:
        Result containing file path on success or IOError on failure
    """
    pass

def sanitize_filename(title: str) -> str:
    """
    Convert video title to valid filename
    
    Args:
        title: Raw video title
        
    Returns:
        Sanitized filename safe for all operating systems
    """
    pass

def handle_filename_conflict(path: Path) -> Path:
    """
    Handle existing file with same name
    
    Args:
        path: Desired file path
        
    Returns:
        Available file path (may append number if conflict exists)
    """
    pass
```

**Responsibilities**:
- Generate filename from video title
- Sanitize filename (remove invalid characters)
- Handle filename conflicts (append numbers if needed)
- Save content to disk
- Return file path on success

## Data Models

### Core Data Types

```python
from dataclasses import dataclass
from typing import List, Optional, Union
from enum import Enum

@dataclass
class TranscriptSegment:
    """Individual segment of transcript with timing"""
    text: str
    start_time: float  # seconds from video start
    duration: float    # segment duration in seconds

@dataclass
class Transcript:
    """Complete transcript with metadata"""
    segments: List[TranscriptSegment]
    language: str
    video_id: str
    
    def get_plain_text(self) -> str:
        """Concatenate all segments into plain text"""
        return " ".join(seg.text for seg in self.segments)
    
    def get_duration(self) -> float:
        """Calculate total video duration"""
        if not self.segments:
            return 0.0
        last_seg = self.segments[-1]
        return last_seg.start_time + last_seg.duration

@dataclass
class KeyPoint:
    """Key point extracted from video with timestamp"""
    text: str
    timestamp: str  # formatted as MM:SS or HH:MM:SS
    start_time: float  # original time in seconds
    relevance_score: float  # 0.0 to 1.0

@dataclass
class Summary:
    """Summary of video content"""
    overview: str  # 2-3 sentence overview
    key_points: List[KeyPoint]

@dataclass
class YouTubeURL:
    """Parsed YouTube URL"""
    video_id: str
    original_url: str

@dataclass
class MarkdownDocument:
    """Generated markdown content"""
    content: str
    video_title: str

class ErrorType(Enum):
    """Types of errors that can occur"""
    INVALID_URL = "invalid_url"
    VIDEO_NOT_FOUND = "video_not_found"
    TRANSCRIPT_NOT_AVAILABLE = "transcript_not_available"
    LANGUAGE_NOT_AVAILABLE = "language_not_available"
    NETWORK_ERROR = "network_error"
    FILE_WRITE_ERROR = "file_write_error"
    API_RATE_LIMIT = "api_rate_limit"

@dataclass
class ProcessingError:
    """Error information"""
    error_type: ErrorType
    message: str
    details: Optional[str] = None
```

### Result Type

```python
from typing import TypeVar, Generic, Union

T = TypeVar('T')
E = TypeVar('E')

@dataclass
class Ok(Generic[T]):
    value: T

@dataclass
class Err(Generic[E]):
    error: E

Result = Union[Ok[T], Err[E]]
```

This Result type enables explicit error handling throughout the pipeline without exceptions.


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### URL Validation Properties

Property 1: Valid YouTube URLs are accepted
*For any* valid YouTube URL (in youtube.com/watch?v= or youtu.be/ format), the validator should successfully validate it and return success
**Validates: Requirements 1.1, 1.4**

Property 2: Video ID extraction consistency
*For any* valid YouTube URL, extracting the video ID should produce the same ID regardless of URL format (youtube.com vs youtu.be)
**Validates: Requirements 1.2**

Property 3: Invalid URLs are rejected with errors
*For any* invalid URL string, the validator should reject it and return a descriptive error message
**Validates: Requirements 1.3**

### Transcript Processing Properties

Property 4: Plain text preserves chronological order
*For any* list of transcript segments, converting to plain text should preserve the chronological order of segments based on start_time
**Validates: Requirements 2.2**

### Summary and Timestamp Properties

Property 5: All key points have timestamps
*For any* generated summary, every key point should have an associated timestamp in the correct format
**Validates: Requirements 3.3**

Property 6: Timestamp format matches video duration
*For any* time value in seconds, if the total duration is less than 3600 seconds, the timestamp should be formatted as MM:SS, otherwise as HH:MM:SS
**Validates: Requirements 3.4**

### Markdown Output Properties

Property 7: Markdown contains all required sections
*For any* generated markdown document, it should contain sections for transcript, overview summary, and key points with timestamps
**Validates: Requirements 4.2, 4.3, 4.4**

Property 8: Markdown is syntactically valid
*For any* generated markdown document, it should be valid markdown with proper headers, lists, and formatting
**Validates: Requirements 4.5**

### Error Handling Properties

Property 9: All errors produce descriptive messages
*For any* error condition encountered during processing, the system should return an error object with a descriptive message
**Validates: Requirements 7.1**

### File Management Properties

Property 10: Successful processing creates output file
*For any* successfully processed video, a markdown file should be created on disk
**Validates: Requirements 8.1**

Property 11: Filenames are generated from titles
*For any* video title, a filename should be generated that is based on the title content
**Validates: Requirements 8.2**

Property 12: Filenames are sanitized
*For any* video title containing invalid filename characters (/, \, :, *, ?, ", <, >, |), the generated filename should have these characters removed or replaced
**Validates: Requirements 8.3**

Property 13: Filename conflicts are resolved
*For any* output filename, if a file with that name already exists, the system should generate a unique filename (e.g., by appending a number)
**Validates: Requirements 8.4**

## Error Handling

The system uses a Result type pattern for explicit error handling without exceptions. Each component returns `Result[T, E]` where T is the success type and E is the error type.

### Error Types and Handling

**URL Validation Errors**:
- `INVALID_URL`: Malformed URL that doesn't match YouTube patterns
  - Message: "Invalid YouTube URL format. Expected youtube.com/watch?v= or youtu.be/ format"
  - Recovery: User provides corrected URL

**Transcript Fetching Errors**:
- `VIDEO_NOT_FOUND`: Video doesn't exist, is private, or is restricted
  - Message: "Video not found or is private/restricted"
  - Recovery: User provides different video URL
  
- `TRANSCRIPT_NOT_AVAILABLE`: Video has no transcript/captions
  - Message: "No transcript available for this video"
  - Recovery: User provides different video with captions
  
- `LANGUAGE_NOT_AVAILABLE`: English transcript not available
  - Message: "English transcript not available for this video"
  - Recovery: User provides video with English captions

**Network Errors**:
- `NETWORK_ERROR`: Connection issues, timeouts
  - Message: "Network error occurred: [details]"
  - Recovery: Retry after checking connection

**API Errors**:
- `API_RATE_LIMIT`: Too many requests to YouTube API
  - Message: "API rate limit exceeded. Please try again later"
  - Recovery: Wait and retry

**File System Errors**:
- `FILE_WRITE_ERROR`: Cannot write to disk
  - Message: "Failed to write output file: [details]"
  - Recovery: Check permissions, disk space

### Error Propagation

Errors propagate through the pipeline using the Result type:

```python
def process_video(url: str) -> Result[Path, ProcessingError]:
    # Validate URL
    url_result = validate_youtube_url(url)
    if isinstance(url_result, Err):
        return url_result
    
    youtube_url = url_result.value
    
    # Fetch transcript
    transcript_result = fetch_transcript(youtube_url.video_id)
    if isinstance(transcript_result, Err):
        return transcript_result
    
    transcript = transcript_result.value
    
    # Generate summary
    summary = generate_summary(transcript)
    
    # Generate markdown
    markdown = generate_markdown(transcript, summary, youtube_url.video_id)
    
    # Save file
    file_result = save_markdown(markdown, youtube_url.video_id)
    return file_result
```

Each step checks for errors and propagates them up the chain. The CLI interface catches errors and displays user-friendly messages.

## Testing Strategy

The testing strategy employs both unit tests and property-based tests to ensure comprehensive coverage.

### Unit Testing

Unit tests focus on:
- Specific examples of URL parsing (youtube.com, youtu.be formats)
- Edge cases: empty transcripts, very long videos, special characters in titles
- Error conditions: invalid URLs, missing transcripts, network failures
- Integration points: API mocking for transcript fetching
- File system operations: writing, conflict resolution

**Example Unit Tests**:
- Test URL validation with specific valid/invalid examples
- Test timestamp formatting for specific durations (59 seconds, 60 seconds, 3599 seconds, 3600 seconds)
- Test filename sanitization with specific problematic characters
- Test error message content for each error type

### Property-Based Testing

Property-based tests verify universal properties across randomized inputs. Each test should run a minimum of 100 iterations.

**Testing Library**: Use `hypothesis` (Python) for property-based testing

**Property Test Configuration**:
- Minimum 100 iterations per test
- Each test tagged with: `# Feature: youtube-transcript-summarizer, Property N: [property text]`
- Use custom generators for domain-specific types (YouTube URLs, transcript segments, etc.)

**Property Test Examples**:

1. **URL Validation** (Property 1, 2, 3):
   - Generate random valid YouTube URLs → all should validate successfully
   - Generate random invalid URLs → all should be rejected
   - Generate same video ID in different URL formats → should extract same ID

2. **Transcript Processing** (Property 4):
   - Generate random transcript segments with timestamps → plain text should maintain order

3. **Timestamp Formatting** (Property 6):
   - Generate random time values → format should match duration rules

4. **Markdown Generation** (Property 7, 8):
   - Generate random transcripts and summaries → markdown should contain all sections
   - Generated markdown should parse as valid markdown

5. **Filename Handling** (Property 12, 13):
   - Generate random titles with invalid characters → filenames should be sanitized
   - Generate existing filenames → conflicts should be resolved uniquely

**Custom Generators**:

```python
from hypothesis import strategies as st

# Generate valid YouTube video IDs (11 characters, alphanumeric + - and _)
video_ids = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_'),
    min_size=11,
    max_size=11
)

# Generate YouTube URLs
youtube_urls = st.one_of(
    st.builds(lambda vid: f"https://www.youtube.com/watch?v={vid}", video_ids),
    st.builds(lambda vid: f"https://youtu.be/{vid}", video_ids)
)

# Generate transcript segments
transcript_segments = st.builds(
    TranscriptSegment,
    text=st.text(min_size=1, max_size=200),
    start_time=st.floats(min_value=0, max_value=7200),
    duration=st.floats(min_value=0.1, max_value=10)
)
```

### Integration Testing

Integration tests verify the complete pipeline:
- End-to-end processing with mocked YouTube API
- File system integration (actual file writing and reading)
- Error handling across component boundaries

### Test Coverage Goals

- Unit test coverage: >80% of code
- Property tests: All 13 correctness properties implemented
- Integration tests: Complete pipeline with success and error paths
- Edge cases: Empty inputs, maximum lengths, special characters

## Dependencies

**Core Libraries**:
- `youtube-transcript-api`: Fetch transcripts from YouTube
- `hypothesis`: Property-based testing framework
- Python standard library: `argparse`, `pathlib`, `re`, `dataclasses`

**AI/LLM Integration**:
- OpenAI API or Anthropic API for summary generation
- Alternative: Use local models via `transformers` library

**Development Dependencies**:
- `pytest`: Test framework
- `pytest-cov`: Coverage reporting
- `mypy`: Type checking
- `black`: Code formatting
- `ruff`: Linting

## Implementation Notes

**YouTube Transcript API**:
The `youtube-transcript-api` library provides a simple interface:
```python
from youtube_transcript_api import YouTubeTranscriptApi

transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
```

**LLM Integration for Summarization**:
The summarizer component will use an LLM API to analyze transcripts. The prompt structure:
```
Analyze this video transcript and provide:
1. A brief 2-3 sentence overview
2. 5-10 key points with their approximate timestamps

Transcript:
[transcript text with timestamps]
```

**Filename Sanitization**:
Remove or replace: `/ \ : * ? " < > |`
Replace spaces with underscores or hyphens
Limit length to 255 characters (filesystem limit)

**Timestamp Formatting**:
```python
def format_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"
```
