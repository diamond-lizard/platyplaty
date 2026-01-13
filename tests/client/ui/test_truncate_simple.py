#!/usr/bin/env python3
"""Unit tests for truncate_simple function."""

import pytest

from platyplaty.ui.truncation import truncate_simple


class TestTruncateSimpleFits:
    """Tests when text fits within width."""

    def test_exact_fit(self) -> None:
        """Text exactly matching width returns as-is."""
        assert truncate_simple("hello", 5) == "hello"

    def test_shorter_than_width(self) -> None:
        """Text shorter than width returns as-is."""
        assert truncate_simple("hi", 10) == "hi"

    def test_empty_string_fits(self) -> None:
        """Empty string returns as-is."""
        assert truncate_simple("", 5) == ""


class TestTruncateSimpleTruncates:
    """Tests when text is truncated."""

    def test_one_char_over(self) -> None:
        """Text one char over width gets truncated with tilde."""
        assert truncate_simple("hello", 4) == "hel~"

    def test_much_longer(self) -> None:
        """Long text truncated to width-1 plus tilde."""
        assert truncate_simple("very-long-text", 5) == "very~"


class TestTruncateSimpleEdgeCases:
    """Tests for edge cases (TASK-00500, TASK-00600)."""

    def test_width_zero(self) -> None:
        """Width 0 returns empty string."""
        assert truncate_simple("hello", 0) == ""

    def test_width_negative(self) -> None:
        """Negative width returns empty string."""
        assert truncate_simple("hello", -1) == ""

    def test_width_one_with_text(self) -> None:
        """Width 1 returns first char of text."""
        assert truncate_simple("hello", 1) == "h"

    def test_width_one_empty_string(self) -> None:
        """Width 1 with empty string returns tilde."""
        assert truncate_simple("", 1) == "~"

    def test_width_two_long_text(self) -> None:
        """Width 2 with long text returns first char + tilde."""
        assert truncate_simple("hello", 2) == "h~"
