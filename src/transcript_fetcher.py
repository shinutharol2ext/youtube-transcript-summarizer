"""Transcript fetching from YouTube videos."""

from typing import List
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    CouldNotRetrieveTranscript
)

from src.models import (
    Transcript,
    TranscriptSegment,
    ProcessingError,
    ErrorType,
    Ok,
    Err,
    Result
)


def fetch_transcript(video_id: str, language: str = "en", translate_to: str = None) -> Result[Transcript, ProcessingError]:
    """
    Fetch transcript for a YouTube video.
    
    Args:
        video_id: YouTube video identifier
        language: Language code (default: "en")
        translate_to: Target language code for translation (optional)
        
    Returns:
        Result containing Transcript on success or ProcessingError on failure
        
    Errors:
        - TranscriptNotAvailable: Video has no transcript
        - VideoNotFound: Video does not exist or is private
        - LanguageNotAvailable: Requested language not available
        - NetworkError: Connection issues
    """
    try:
        # If translation is requested, use the translation API
        if translate_to and translate_to != language:
            # Get the transcript list to access translation
            transcript_list = YouTubeTranscriptApi().list(video_id)
            transcript_obj = transcript_list.find_transcript([language])
            translated = transcript_obj.translate(translate_to)
            fetched_transcript = translated.fetch()
        else:
            # Fetch transcript from YouTube using the new API
            # The new API returns a FetchedTranscript object with snippets
            fetched_transcript = YouTubeTranscriptApi().fetch(video_id, languages=[language])
        
        # Convert to our data model
        segments = [
            TranscriptSegment(
                text=snippet.text,
                start_time=snippet.start,
                duration=snippet.duration
            )
            for snippet in fetched_transcript.snippets
        ]
        
        transcript = Transcript(
            segments=segments,
            language=translate_to if translate_to else language,
            video_id=video_id
        )
        
        return Ok(transcript)
        
    except VideoUnavailable as e:
        error = ProcessingError(
            error_type=ErrorType.VIDEO_NOT_FOUND,
            message="Video not found or is private/restricted",
            details=str(e)
        )
        return Err(error)
    
    except TranscriptsDisabled as e:
        error = ProcessingError(
            error_type=ErrorType.TRANSCRIPT_NOT_AVAILABLE,
            message="No transcript available for this video",
            details=str(e)
        )
        return Err(error)
    
    except NoTranscriptFound as e:
        error = ProcessingError(
            error_type=ErrorType.LANGUAGE_NOT_AVAILABLE,
            message=f"Transcript not available in the requested language",
            details=str(e)
        )
        return Err(error)
    
    except CouldNotRetrieveTranscript as e:
        error = ProcessingError(
            error_type=ErrorType.TRANSCRIPT_NOT_AVAILABLE,
            message="Could not retrieve transcript for this video",
            details=str(e)
        )
        return Err(error)
    
    except Exception as e:
        # Catch network errors and other unexpected issues
        error = ProcessingError(
            error_type=ErrorType.NETWORK_ERROR,
            message=f"Network error occurred: {str(e)}",
            details=str(e)
        )
        return Err(error)


def get_plain_text(transcript: Transcript) -> str:
    """
    Convert transcript segments to plain text.
    
    Args:
        transcript: Transcript object with segments
        
    Returns:
        Plain text string with all spoken content
    """
    return " ".join(segment.text for segment in transcript.segments)
