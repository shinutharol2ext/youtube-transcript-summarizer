"""Tests for file writing component."""

from hypothesis import given, strategies as st
import pytest
import tempfile
import shutil
from pathlib import Path

from src.file_writer import save_markdown, sanitize_filename, handle_filename_conflict
from src.models import MarkdownDocument, Ok, Err


class TestFilenameSanitization:
    """Tests for filename sanitization."""
    
    # Feature: youtube-transcript-summarizer, Property 12: Filenames are sanitized
    @given(st.text(min_size=1, max_size=100))
    def test_filenames_are_sanitized(self, title: str):
        """
        Property 12: Filenames are sanitized.
        
        For any video title containing invalid filename characters
        (/, \, :, *, ?, ", <, >, |), the generated filename should
        have these characters removed or replaced.
        
        **Validates: Requirements 8.3**
        """
        filename = sanitize_filename(title)
        
        # Check that invalid characters are removed
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            assert char not in filename, f"Invalid character '{char}' found in filename: {filename}"
        
        # Filename should not be empty
        assert len(filename) > 0
        
        # Filename should not exceed 255 characters
        assert len(filename) <= 255


class TestFilenameConflictResolution:
    """Tests for filename conflict resolution."""
    
    # Feature: youtube-transcript-summarizer, Property 13: Filename conflicts are resolved
    def test_filename_conflicts_are_resolved(self):
        """
        Property 13: Filename conflicts are resolved.
        
        For any output filename, if a file with that name already exists,
        the system should generate a unique filename (e.g., by appending a number).
        
        **Validates: Requirements 8.4**
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create initial file
            test_file = tmppath / "test.md"
            test_file.write_text("content")
            
            # Handle conflict
            new_path = handle_filename_conflict(test_file)
            
            # Should return a different path
            assert new_path != test_file
            assert not new_path.exists()
            assert new_path.name == "test_1.md"


class TestSuccessfulFileCreation:
    """Tests for successful file creation."""
    
    # Feature: youtube-transcript-summarizer, Property 10: Successful processing creates output file
    def test_successful_processing_creates_output_file(self):
        """
        Property 10: Successful processing creates output file.
        
        For any successfully processed video, a markdown file
        should be created on disk.
        
        **Validates: Requirements 8.1**
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            document = MarkdownDocument(
                content="# Test\n\nContent",
                video_title="Test Video"
            )
            
            result = save_markdown(document, "Test Video", output_dir=tmpdir)
            
            assert isinstance(result, Ok)
            assert result.value.exists()
            assert result.value.is_file()
            
            # Verify content
            content = result.value.read_text()
            assert content == "# Test\n\nContent"


class TestFilenameGeneration:
    """Tests for filename generation."""
    
    # Feature: youtube-transcript-summarizer, Property 11: Filenames are generated from titles
    @given(st.text(min_size=1, max_size=50, alphabet=st.characters(
        blacklist_categories=('Cs',),
        blacklist_characters='/\\:*?"<>|\n\r\t'
    )))
    def test_filenames_are_generated_from_titles(self, title: str):
        """
        Property 11: Filenames are generated from titles.
        
        For any video title, a filename should be generated
        that is based on the title content.
        
        **Validates: Requirements 8.2**
        """
        if not title.strip():
            return  # Skip empty titles
        
        filename = sanitize_filename(title)
        
        # Filename should be related to title
        # (contains some characters from title or is default)
        assert len(filename) > 0
        assert filename == "transcript" or any(
            c.lower() in filename.lower() for c in title if c.isalnum()
        )


class TestFileWriterUnitTests:
    """Unit tests for file writing."""
    
    def test_sanitize_filename_removes_invalid_chars(self):
        """Test that invalid characters are removed."""
        title = "My Video: Part 1 / Test * File?"
        filename = sanitize_filename(title)
        
        assert filename == "My_Video_Part_1_Test_File"
    
    def test_sanitize_filename_replaces_spaces(self):
        """Test that spaces are replaced with underscores."""
        title = "My Test Video"
        filename = sanitize_filename(title)
        
        assert filename == "My_Test_Video"
    
    def test_sanitize_filename_limits_length(self):
        """Test that filename length is limited to 255 characters."""
        title = "a" * 300
        filename = sanitize_filename(title)
        
        assert len(filename) <= 255
    
    def test_sanitize_filename_empty_string(self):
        """Test that empty string returns default."""
        filename = sanitize_filename("")
        assert filename == "transcript"
    
    def test_sanitize_filename_only_invalid_chars(self):
        """Test that string with only invalid chars returns default."""
        filename = sanitize_filename("///:::***")
        assert filename == "transcript"
    
    def test_handle_filename_conflict_no_conflict(self):
        """Test that no conflict returns original path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            test_file = tmppath / "test.md"
            
            result = handle_filename_conflict(test_file)
            
            assert result == test_file
    
    def test_handle_filename_conflict_with_conflict(self):
        """Test that conflict appends number."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create initial file
            test_file = tmppath / "test.md"
            test_file.write_text("content")
            
            # Handle conflict
            result = handle_filename_conflict(test_file)
            
            assert result == tmppath / "test_1.md"
    
    def test_handle_filename_conflict_multiple_conflicts(self):
        """Test that multiple conflicts increment number."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create multiple files
            (tmppath / "test.md").write_text("content")
            (tmppath / "test_1.md").write_text("content")
            (tmppath / "test_2.md").write_text("content")
            
            # Handle conflict
            result = handle_filename_conflict(tmppath / "test.md")
            
            assert result == tmppath / "test_3.md"
    
    def test_save_markdown_creates_file(self):
        """Test that save_markdown creates a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            document = MarkdownDocument(
                content="# Title\n\nContent",
                video_title="My Video"
            )
            
            result = save_markdown(document, "My Video", output_dir=tmpdir)
            
            assert isinstance(result, Ok)
            assert result.value.name == "My_Video.md"
            assert result.value.exists()
    
    def test_save_markdown_handles_conflicts(self):
        """Test that save_markdown handles filename conflicts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create initial file
            (tmppath / "My_Video.md").write_text("old content")
            
            document = MarkdownDocument(
                content="# Title\n\nNew content",
                video_title="My Video"
            )
            
            result = save_markdown(document, "My Video", output_dir=tmpdir)
            
            assert isinstance(result, Ok)
            assert result.value.name == "My_Video_1.md"
            assert result.value.read_text() == "# Title\n\nNew content"
    
    def test_save_markdown_adds_md_extension(self):
        """Test that .md extension is added if missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            document = MarkdownDocument(
                content="Content",
                video_title="Video"
            )
            
            result = save_markdown(document, "Video", output_dir=tmpdir)
            
            assert isinstance(result, Ok)
            assert result.value.suffix == ".md"
