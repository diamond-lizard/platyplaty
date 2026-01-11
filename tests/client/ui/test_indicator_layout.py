#!/usr/bin/env python3
"""Unit tests for calculate_indicator_layout function."""

import pytest

from platyplaty.ui.indicators import calculate_indicator_layout


class TestIndicatorLayoutFits:
    """Tests for layout calculation when content fits in pane width."""

    def test_right_justifies_indicator(self) -> None:
        """Indicator is right-justified within pane width."""
        result = calculate_indicator_layout("file.milk", "1.5 K", 20)
        assert result == "file.milk      1.5 K"
        assert len(result) == 20

    def test_minimum_one_space_gap(self) -> None:
        """At least one space between name and indicator."""
        result = calculate_indicator_layout("name", "42", 10)
        assert result == "name    42"
        assert len(result) == 10

    def test_exact_fit(self) -> None:
        """Content exactly fits pane width with minimum gap."""
        result = calculate_indicator_layout("abc", "12", 6)
        assert result == "abc 12"
        assert len(result) == 6

    def test_empty_name(self) -> None:
        """Empty name with indicator."""
        result = calculate_indicator_layout("", "42", 10)
        assert result == "        42"
        assert len(result) == 10

    def test_empty_indicator(self) -> None:
        """Name with empty indicator."""
        result = calculate_indicator_layout("file.milk", "", 15)
        assert result == "file.milk      "
        assert len(result) == 15


class TestIndicatorLayoutOverflow:
    """Tests for layout calculation when content exceeds pane width."""

    def test_overflow_single_space(self) -> None:
        """Content exceeds pane width, uses single space gap."""
        result = calculate_indicator_layout("very-long-name.milk", "1.5 K", 10)
        assert result == "very-long-name.milk 1.5 K"
        assert " " in result

    def test_overflow_preserves_content(self) -> None:
        """All content preserved even when overflowing."""
        name = "extremely-long-preset-name.milk"
        indicator = "-> 42"
        result = calculate_indicator_layout(name, indicator, 20)
        assert name in result
        assert indicator in result

    def test_zero_width(self) -> None:
        """Zero pane width causes overflow."""
        result = calculate_indicator_layout("file", "42", 0)
        assert result == "file 42"
