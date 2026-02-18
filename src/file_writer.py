"""File writing utilities for saving markdown documents."""

import re
from pathlib import Path
from typing import Optional

from src.models import MarkdownDocument, ProcessingError, ErrorType, Ok, Err, Result


def save_markdown(
    document: MarkdownDocument,
    video_title: str,
    output_dir: str = "."
) -> Result[Path, ProcessingError]:
    """
    Save markdown document to file.
    
    Args:
        document: Markdown content to save
        video_title: Video title for filename generation
        output_dir: Directory to save file (default: current directory)
        
    Returns:
        Result containing file path on success or ProcessingError on failure
    """
    try:
        # Generate filename from video title
        filename = sanitize_filename(video_title)
        
        # Ensure .md extension
        if not filename.endswith('.md'):
            filename += '.md'
        
        # Create full path
        output_path = Path(output_dir) / filename
        
        # Handle filename conflicts
        output_path = handle_filename_conflict(output_path)
        
        # Write content to file
        output_path.write_text(document.content, encoding='utf-8')
        
        return Ok(output_path)
        
    except Exception as e:
        error = ProcessingError(
            error_type=ErrorType.FILE_WRITE_ERROR,
            message=f"Failed to write output file: {str(e)}",
            details=str(e)
        )
        return Err(error)


def sanitize_filename(title: str) -> str:
    """
    Convert video title to valid filename.
    
    Args:
        title: Raw video title
        
    Returns:
        Sanitized filename safe for all operating systems
    """
    if not title or not title.strip():
        return "transcript"
    
    # Remove or replace invalid characters: / \ : * ? " < > |
    sanitized = re.sub(r'[/\\:*?"<>|]', '', title)
    
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    
    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Strip leading/trailing underscores
    sanitized = sanitized.strip('_')
    
    # Limit length to 255 characters (filesystem limit)
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    
    # If empty or contains no alphanumeric characters after sanitization, use default
    if not sanitized or not any(c.isalnum() for c in sanitized):
        return "transcript"
    
    return sanitized


def handle_filename_conflict(path: Path) -> Path:
    """
    Handle existing file with same name.
    
    Args:
        path: Desired file path
        
    Returns:
        Available file path (may append number if conflict exists)
    """
    if not path.exists():
        return path
    
    # File exists, find next available number
    base_path = path.parent
    stem = path.stem
    suffix = path.suffix
    
    counter = 1
    while True:
        new_path = base_path / f"{stem}_{counter}{suffix}"
        if not new_path.exists():
            return new_path
        counter += 1
