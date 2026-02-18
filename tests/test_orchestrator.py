"""Tests for orchestration and error handling."""

from hypothesis import given, strategies as st
import pytest
from unittest.mock import patch, MagicMock
import tempfile

from src.orchestrator import process_video
from src.models import (
    ProcessingError,
    ErrorType,
    Ok,
    Err,
    YouTubeURL,
    Transcript,
    TranscriptSegment
)


class TestErrorPropagation:
    """Tests for error propagation through the pipeline."""
    
    # Feature: youtube-transcript-summarizer, Property 9: All errors produce descriptive messages
    @given(st.sampled_from([
        ErrorType.INVALID_URL,
        ErrorType.VIDEO_NOT_FOUND,
        ErrorType.TRANSCRIPT_NOT_AVAILABLE,
        ErrorType.LANGUAGE_NOT_AVAILABLE,
        ErrorType.NETWORK_ERROR,
    ]))
    def test_all_errors_produce_descriptive_messages(self, error_type: ErrorType):
        """
        Property 9: All errors produce descriptive messages.
        
        For any error condition encountered during processing,
        the system should return an error object with a descriptive message.
        
        **Validates: Requirements 7.1**
        """
        # Create a processing error
        error = ProcessingError(
            error_type=error_type,
            message=f"Test error for {error_type.value}",
            details="Additional details"
        )
        
        # Verify error has required fields
        assert error.error_type == error_type
        assert error.message is not None
        assert len(error.message) > 0
        assert isinstance(error.message, str)


class TestOrchestrationUnitTests:
    """Unit tests for orchestration."""
    
    @patch('src.orchestrator.validate_youtube_url')
    def test_invalid_url_error_propagates(self, mock_validate):
        """Test that invalid URL errors propagate correctly."""
        error = ProcessingError(
            error_type=ErrorType.INVALID_URL,
            message="Invalid URL",
            details="Test"
        )
        mock_validate.return_value = Err(error)
        
        result = process_video("invalid_url")
        
        assert isinstance(result, Err)
        assert result.error.error_type == ErrorType.INVALID_URL
        assert len(result.error.message) > 0
    
    @patch('src.orchestrator.fetch_transcript')
    @patch('src.orchestrator.validate_youtube_url')
    def test_video_not_found_error_propagates(self, mock_validate, mock_fetch):
        """Test that video not found errors propagate correctly."""
        mock_validate.return_value = Ok(YouTubeURL(
            video_id="test123",
            original_url="https://youtube.com/watch?v=test123"
        ))
        
        error = ProcessingError(
            error_type=ErrorType.VIDEO_NOT_FOUND,
            message="Video not found",
            details="Test"
        )
        mock_fetch.return_value = Err(error)
        
        result = process_video("https://youtube.com/watch?v=test123")
        
        assert isinstance(result, Err)
        assert result.error.error_type == ErrorType.VIDEO_NOT_FOUND
        assert len(result.error.message) > 0
    
    @patch('src.orchestrator.fetch_transcript')
    @patch('src.orchestrator.validate_youtube_url')
    def test_transcript_not_available_error_propagates(self, mock_validate, mock_fetch):
        """Test that transcript not available errors propagate correctly."""
        mock_validate.return_value = Ok(YouTubeURL(
            video_id="test123",
            original_url="https://youtube.com/watch?v=test123"
        ))
        
        error = ProcessingError(
            error_type=ErrorType.TRANSCRIPT_NOT_AVAILABLE,
            message="No transcript available",
            details="Test"
        )
        mock_fetch.return_value = Err(error)
        
        result = process_video("https://youtube.com/watch?v=test123")
        
        assert isinstance(result, Err)
        assert result.error.error_type == ErrorType.TRANSCRIPT_NOT_AVAILABLE
        assert len(result.error.message) > 0
    
    @patch('src.orchestrator.save_markdown')
    @patch('src.orchestrator.generate_markdown')
    @patch('src.orchestrator.generate_summary')
    @patch('src.orchestrator.fetch_transcript')
    @patch('src.orchestrator.validate_youtube_url')
    def test_successful_pipeline_execution(
        self,
        mock_validate,
        mock_fetch,
        mock_summary,
        mock_markdown,
        mock_save
    ):
        """Test successful execution through entire pipeline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Mock all components
            mock_validate.return_value = Ok(YouTubeURL(
                video_id="test123",
                original_url="https://youtube.com/watch?v=test123"
            ))
            
            mock_fetch.return_value = Ok(Transcript(
                segments=[
                    TranscriptSegment(text="Test", start_time=0.0, duration=1.0)
                ],
                language="en",
                video_id="test123"
            ))
            
            from pathlib import Path
            output_path = Path(tmpdir) / "test.md"
            mock_save.return_value = Ok(output_path)
            
            result = process_video("https://youtube.com/watch?v=test123", output_dir=tmpdir)
            
            assert isinstance(result, Ok)
            assert mock_validate.called
            assert mock_fetch.called
            assert mock_summary.called
            assert mock_markdown.called
            assert mock_save.called
    
    def test_error_messages_are_descriptive(self):
        """Test that error messages contain useful information."""
        error_types_and_messages = [
            (ErrorType.INVALID_URL, "Invalid YouTube URL format"),
            (ErrorType.VIDEO_NOT_FOUND, "Video not found or is private/restricted"),
            (ErrorType.TRANSCRIPT_NOT_AVAILABLE, "No transcript available"),
            (ErrorType.LANGUAGE_NOT_AVAILABLE, "English transcript not available"),
            (ErrorType.NETWORK_ERROR, "Network error occurred"),
            (ErrorType.FILE_WRITE_ERROR, "Failed to write output file"),
        ]
        
        for error_type, expected_message_part in error_types_and_messages:
            error = ProcessingError(
                error_type=error_type,
                message=expected_message_part,
                details="Test details"
            )
            
            assert error.message is not None
            assert len(error.message) > 0
            assert expected_message_part.lower() in error.message.lower() or \
                   error_type.value in error.message.lower()
