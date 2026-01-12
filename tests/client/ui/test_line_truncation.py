#!/usr/bin/env python3
"""Tests for line truncation (TASK-3510)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.file_browser_file_utils import truncate_line


class TestLineTruncation:
    """Tests for truncate_line function."""

    def test_short_line_unchanged(self) -> None:
        """Line shorter than width is returned as-is."""
        result = truncate_line("hello", 10)
        assert result == "hello"

    def test_exact_width_unchanged(self) -> None:
        """Line exactly at width is returned as-is."""
        result = truncate_line("hello", 5)
        assert result == "hello"

    def test_long_line_truncated(self) -> None:
        """Line longer than width is truncated."""
        result = truncate_line("hello world", 5)
        assert result == "hello"

    def test_tab_expanded_to_4_spaces(self) -> None:
        """Tabs are expanded to 4 spaces before truncation."""
        result = truncate_line("	hello", 20)
        assert result == "    hello"

    def test_tab_expansion_affects_width(self) -> None:
        """Tab expansion is considered for width calculation."""
        result = truncate_line("	hello", 6)
        assert result == "    he"

    def test_wide_unicode_character(self) -> None:
        """Wide Unicode characters (CJK) take 2 cells."""
        result = truncate_line("Hello 世界", 10)
        assert result == "Hello 世界"

    def test_wide_unicode_truncation(self) -> None:
        """Wide Unicode characters are not split."""
        result = truncate_line("Hello 世界", 7)
        assert result == "Hello "

    def test_empty_line(self) -> None:
        """Empty line returns empty string."""
        result = truncate_line("", 10)
        assert result == ""

    def test_zero_width(self) -> None:
        """Zero width returns empty string."""
        result = truncate_line("hello", 0)
        assert result == ""
