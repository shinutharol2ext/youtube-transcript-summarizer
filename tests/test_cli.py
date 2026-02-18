"""Tests for CLI interface."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile

from src.cli import parse_arguments, main
from src.models import Ok, Err, ProcessingError, ErrorType


class TestCLIArgumentParsing:
    """Tests for CLI argument parsing."""
    
    def test_parse_arguments_with_url_only(self):
        """Test parsing with just URL argument."""
        args = parse_arguments(['https://youtube.com/watch?v=test123'])
        
        assert args.url == 'https://youtube.com/watch?v=test123'
        assert args.output_dir == '.'
        assert args.api_key is None
    
    def test_parse_arguments_with_output_dir(self):
        """Test parsing with output directory."""
        args = parse_arguments(['https://youtube.com/watch?v=test123', '-o', '/tmp/output'])
        
        assert args.url == 'https://youtube.com/watch?v=test123'
        assert args.output_dir == '/tmp/output'
    
    def test_parse_arguments_with_api_key(self):
        """Test parsing with API key."""
        args = parse_arguments(['https://youtube.com/watch?v=test123', '--api-key', 'test_key'])
        
        assert args.url == 'https://youtube.com/watch?v=test123'
        assert args.api_key == 'test_key'
    
    def test_parse_arguments_with_all_options(self):
        """Test parsing with all options."""
        args = parse_arguments([
            'https://youtube.com/watch?v=test123',
            '-o', '/tmp/output',
            '--api-key', 'test_key'
        ])
        
        assert args.url == 'https://youtube.com/watch?v=test123'
        assert args.output_dir == '/tmp/output'
        assert args.api_key == 'test_key'


class TestCLIIntegration:
    """Integration tests for CLI."""
    
    @patch('src.cli.process_video')
    def test_main_success(self, mock_process):
        """Test successful CLI execution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.md"
            mock_process.return_value = Ok(output_path)
            
            exit_code = main(['https://youtube.com/watch?v=test123'])
            
            assert exit_code == 0
            assert mock_process.called
    
    @patch('src.cli.process_video')
    def test_main_invalid_url_error(self, mock_process):
        """Test CLI with invalid URL error."""
        error = ProcessingError(
            error_type=ErrorType.INVALID_URL,
            message="Invalid URL",
            details="Test"
        )
        mock_process.return_value = Err(error)
        
        exit_code = main(['invalid_url'])
        
        assert exit_code == 1
        assert mock_process.called
    
    @patch('src.cli.process_video')
    def test_main_video_not_found_error(self, mock_process):
        """Test CLI with video not found error."""
        error = ProcessingError(
            error_type=ErrorType.VIDEO_NOT_FOUND,
            message="Video not found",
            details="Test"
        )
        mock_process.return_value = Err(error)
        
        exit_code = main(['https://youtube.com/watch?v=test123'])
        
        assert exit_code == 1
    
    @patch('src.cli.process_video')
    def test_main_with_output_dir(self, mock_process):
        """Test CLI with custom output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.md"
            mock_process.return_value = Ok(output_path)
            
            exit_code = main(['https://youtube.com/watch?v=test123', '-o', tmpdir])
            
            assert exit_code == 0
            mock_process.assert_called_once_with(
                'https://youtube.com/watch?v=test123',
                tmpdir,
                source_lang=None,
                translate_to=None
            )
    
    @patch('src.cli.process_video')
    def test_main_handles_keyboard_interrupt(self, mock_process):
        """Test CLI handles keyboard interrupt gracefully."""
        mock_process.side_effect = KeyboardInterrupt()
        
        exit_code = main(['https://youtube.com/watch?v=test123'])
        
        assert exit_code == 130
    
    @patch('src.cli.process_video')
    def test_main_handles_unexpected_exception(self, mock_process):
        """Test CLI handles unexpected exceptions."""
        mock_process.side_effect = RuntimeError("Unexpected error")
        
        exit_code = main(['https://youtube.com/watch?v=test123'])
        
        assert exit_code == 1
    
    @patch('src.cli.process_video')
    def test_main_displays_error_details(self, mock_process, capsys):
        """Test that CLI displays error details."""
        error = ProcessingError(
            error_type=ErrorType.NETWORK_ERROR,
            message="Network error occurred",
            details="Connection timeout"
        )
        mock_process.return_value = Err(error)
        
        exit_code = main(['https://youtube.com/watch?v=test123'])
        
        captured = capsys.readouterr()
        assert "Network error occurred" in captured.err
        assert "Connection timeout" in captured.err
        assert exit_code == 1
