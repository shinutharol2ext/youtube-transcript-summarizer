"""URL validation and parsing for YouTube videos."""

import re
from typing import Optional
from urllib.parse import urlparse, parse_qs

from src.models import YouTubeURL, ProcessingError, ErrorType, Ok, Err, Result


def extract_video_id(url: str) -> Optional[str]:
    """
    Extract video ID from various YouTube URL formats.
    
    Supports:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/watch?v=VIDEO_ID&other=params
    - https://www.youtube.com/shorts/VIDEO_ID
    
    Args:
        url: YouTube URL string
        
    Returns:
        Video ID if found, None otherwise
    """
    if not url:
        return None
    
    try:
        parsed = urlparse(url)
        
        # Handle youtu.be format
        if parsed.netloc in ('youtu.be', 'www.youtu.be'):
            # Video ID is in the path
            video_id = parsed.path.lstrip('/')
            if video_id:
                return video_id
        
        # Handle youtube.com formats
        elif parsed.netloc in ('youtube.com', 'www.youtube.com'):
            # Handle /watch format
            if parsed.path == '/watch':
                # Video ID is in the 'v' query parameter
                query_params = parse_qs(parsed.query)
                if 'v' in query_params and query_params['v']:
                    return query_params['v'][0]
            
            # Handle /shorts format
            elif parsed.path.startswith('/shorts/'):
                # Video ID is in the path after /shorts/
                video_id = parsed.path.replace('/shorts/', '')
                if video_id:
                    return video_id
        
        return None
    except Exception:
        return None


def validate_youtube_url(url: str) -> Result[YouTubeURL, ProcessingError]:
    """
    Validate and parse a YouTube URL.
    
    Args:
        url: Raw URL string from user input
        
    Returns:
        Result containing YouTubeURL on success or ProcessingError on failure
    """
    video_id = extract_video_id(url)
    
    if video_id is None:
        error = ProcessingError(
            error_type=ErrorType.INVALID_URL,
            message="Invalid YouTube URL format. Expected youtube.com/watch?v= or youtu.be/ format",
            details=f"Provided URL: {url}"
        )
        return Err(error)
    
    youtube_url = YouTubeURL(video_id=video_id, original_url=url)
    return Ok(youtube_url)
