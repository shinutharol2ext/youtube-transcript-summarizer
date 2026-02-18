"""Tests for timestamp formatting."""

from hypothesis import given, strategies as st
import pytest
import re

from src.timestamp_formatter import format_timestamp


class TestTimestampFormatting:
    """Tests for timestamp formatting."""
    
    # Feature: youtube-transcript-summarizer, Property 6: Timestamp format matches video duration
    @given(st.floats(min_value=0, max_value=3599.99))
    def test_timestamp_format_under_one_hour(self, seconds: float):
        """
        Property 6: Timestamp format matches video duration (under 1 hour).
        
        For any time value in seconds less than 3600 seconds,
        the timestamp should be formatted as MM:SS.
        
        **Validates: Requirements 3.4**
        """
        timestamp = format_timestamp(seconds)
        
        # Should match MM:SS format
        assert re.match(r'^\d{2}:\d{2}$', timestamp), f"Expected MM:SS format, got {timestamp}"
        
        # Verify it doesn't have hours
        assert timestamp.count(':') == 1
    
    @given(st.floats(min_value=3600, max_value=86400))
    def test_timestamp_format_one_hour_or_more(self, seconds: float):
        """
        Property 6: Timestamp format matches video duration (1 hour or more).
        
        For any time value in seconds of 3600 or more,
        the timestamp should be formatted as HH:MM:SS.
        
        **Validates: Requirements 3.4**
        """
        timestamp = format_timestamp(seconds)
        
        # Should match HH:MM:SS format
        assert re.match(r'^\d{2}:\d{2}:\d{2}$', timestamp), f"Expected HH:MM:SS format, got {timestamp}"
        
        # Verify it has hours
        assert timestamp.count(':') == 2


class TestTimestampFormattingUnitTests:
    """Unit tests for timestamp formatting with specific examples."""
    
    def test_format_59_seconds(self):
        """Test formatting 59 seconds (edge case before 1 minute)."""
        timestamp = format_timestamp(59)
        assert timestamp == "00:59"
    
    def test_format_60_seconds(self):
        """Test formatting 60 seconds (exactly 1 minute)."""
        timestamp = format_timestamp(60)
        assert timestamp == "01:00"
    
    def test_format_3599_seconds(self):
        """Test formatting 3599 seconds (edge case before 1 hour)."""
        timestamp = format_timestamp(3599)
        assert timestamp == "59:59"
    
    def test_format_3600_seconds(self):
        """Test formatting 3600 seconds (exactly 1 hour)."""
        timestamp = format_timestamp(3600)
        assert timestamp == "01:00:00"
    
    def test_format_0_seconds(self):
        """Test formatting 0 seconds."""
        timestamp = format_timestamp(0)
        assert timestamp == "00:00"
    
    def test_format_fractional_seconds(self):
        """Test formatting fractional seconds (should round down)."""
        timestamp = format_timestamp(125.7)
        assert timestamp == "02:05"
    
    def test_format_long_video(self):
        """Test formatting a long video (2 hours, 15 minutes, 30 seconds)."""
        timestamp = format_timestamp(8130)  # 2:15:30
        assert timestamp == "02:15:30"
    
    def test_format_preserves_leading_zeros(self):
        """Test that leading zeros are preserved."""
        timestamp = format_timestamp(5)
        assert timestamp == "00:05"
        
        timestamp = format_timestamp(65)
        assert timestamp == "01:05"
        
        timestamp = format_timestamp(3605)
        assert timestamp == "01:00:05"
