#!/usr/bin/env python3
"""Unit tests for playlist entry truncation behavior.

Tests that playlist entries are truncated correctly when they
exceed the available width, using tilde as the indicator.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.truncation import truncate_simple


class TestTruncateSimple:
    """Tests for the truncate_simple function used by playlist view."""

    def test_short_text_unchanged(self) -> None:
        """Text shorter than width is unchanged."""
        result = truncate_simple("cool.milk", 20)
        assert result == "cool.milk"

    def test_exact_width_unchanged(self) -> None:
        """Text exactly at width is unchanged."""
        result = truncate_simple("cool.milk", 9)
        assert result == "cool.milk"

    def test_long_text_truncated_with_tilde(self) -> None:
        """Text longer than width is truncated with tilde."""
        result = truncate_simple("very-long-preset-name.milk", 15)
        assert result == "very-long-pres~"
        assert len(result) == 15

    def test_width_zero_returns_empty(self) -> None:
        """Width zero returns empty string."""
        result = truncate_simple("cool.milk", 0)
        assert result == ""

    def test_width_one_returns_first_char(self) -> None:
        """Width one returns first character."""
        result = truncate_simple("cool.milk", 1)
        assert result == "c"

    def test_width_two_truncates_to_one_plus_tilde(self) -> None:
        """Width two returns one char plus tilde."""
        result = truncate_simple("cool.milk", 2)
        assert result == "c~"

    def test_empty_text_with_width_one(self) -> None:
        """Empty text with width one returns tilde."""
        result = truncate_simple("", 1)
        assert result == "~"

    def test_empty_text_with_larger_width(self) -> None:
        """Empty text with larger width returns empty string."""
        result = truncate_simple("", 10)
        assert result == ""
