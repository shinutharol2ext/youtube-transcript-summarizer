"""Timestamp formatting utilities."""


def format_timestamp(seconds: float) -> str:
    """
    Format seconds into MM:SS or HH:MM:SS.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted timestamp string
    """
    # Convert to integer seconds
    total_seconds = int(seconds)
    
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    
    if hours > 0:
        # Format as HH:MM:SS for videos 1 hour or longer
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        # Format as MM:SS for videos under 1 hour
        return f"{minutes:02d}:{secs:02d}"
