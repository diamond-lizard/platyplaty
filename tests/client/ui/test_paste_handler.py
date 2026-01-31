#!/usr/bin/env python3
"""Tests for paste_handler module."""


from platyplaty.ui.paste_handler import process_paste_text


class TestProcessPasteText:
    """Tests for process_paste_text function."""

    def test_normal_text_unchanged(self) -> None:
        """Normal text without leading/trailing whitespace is unchanged."""
        assert process_paste_text("hello world") == "hello world"

    def test_leading_whitespace_stripped(self) -> None:
        """Leading whitespace is stripped."""
        assert process_paste_text("  hello") == "hello"

    def test_trailing_whitespace_stripped(self) -> None:
        """Trailing whitespace is stripped."""
        assert process_paste_text("hello  ") == "hello"

    def test_both_leading_and_trailing_stripped(self) -> None:
        """Both leading and trailing whitespace are stripped."""
        assert process_paste_text("  hello  ") == "hello"

    def test_internal_whitespace_preserved(self) -> None:
        """Internal whitespace is preserved."""
        assert process_paste_text("hello   world") == "hello   world"

    def test_empty_string_returns_empty(self) -> None:
        """Empty string returns empty string."""
        assert process_paste_text("") == ""

    def test_whitespace_only_returns_empty(self) -> None:
        """Whitespace-only string returns empty string."""
        assert process_paste_text("   ") == ""

    def test_internal_newlines_preserved(self) -> None:
        """Text with internal newlines is preserved after strip."""
        assert process_paste_text("  line1\nline2  ") == "line1\nline2"

    def test_internal_tabs_preserved(self) -> None:
        """Text with internal tabs is preserved after strip."""
        assert process_paste_text("  col1\tcol2  ") == "col1\tcol2"
