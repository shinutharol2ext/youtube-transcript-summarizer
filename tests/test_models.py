"""Tests for data models."""

from hypothesis import given, strategies as st
import pytest

from src.models import Ok, Err, Result


class TestResultType:
    """Tests for Result type (Ok/Err)."""
    
    @given(st.integers())
    def test_ok_preserves_integer_values(self, value: int):
        """Property: Ok preserves integer values."""
        result = Ok(value)
        assert result.value == value
    
    @given(st.text())
    def test_ok_preserves_string_values(self, value: str):
        """Property: Ok preserves string values."""
        result = Ok(value)
        assert result.value == value
    
    @given(st.integers())
    def test_err_preserves_integer_values(self, error: int):
        """Property: Err preserves integer error values."""
        result = Err(error)
        assert result.error == error
    
    @given(st.text())
    def test_err_preserves_string_values(self, error: str):
        """Property: Err preserves string error values."""
        result = Err(error)
        assert result.error == error
    
    def test_ok_and_err_are_distinct(self):
        """Ok and Err are distinct types."""
        ok_result = Ok(42)
        err_result = Err("error")
        
        assert isinstance(ok_result, Ok)
        assert isinstance(err_result, Err)
        assert not isinstance(ok_result, Err)
        assert not isinstance(err_result, Ok)
