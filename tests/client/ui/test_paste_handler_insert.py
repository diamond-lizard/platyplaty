#!/usr/bin/env python3
"""Tests for paste_handler insertion functions."""

import pytest

from platyplaty.ui.paste_handler import handle_paste, insert_text_at_cursor


class TestInsertTextAtCursor:
    """Tests for insert_text_at_cursor function."""

    def test_insert_at_beginning(self) -> None:
        """Insert text at beginning of string."""
        result = insert_text_at_cursor("world", 0, "hello ")
        assert result == ("hello world", 6)

    def test_insert_at_end(self) -> None:
        """Insert text at end of string."""
        result = insert_text_at_cursor("hello", 5, " world")
        assert result == ("hello world", 11)

    def test_insert_in_middle(self) -> None:
        """Insert text in middle of string."""
        result = insert_text_at_cursor("helloworld", 5, " ")
        assert result == ("hello world", 6)

    def test_insert_into_empty_string(self) -> None:
        """Insert text into empty string."""
        result = insert_text_at_cursor("", 0, "hello")
        assert result == ("hello", 5)

    def test_insert_empty_string(self) -> None:
        """Insert empty string returns unchanged text and cursor."""
        result = insert_text_at_cursor("hello", 3, "")
        assert result == ("hello", 3)

    def test_cursor_position_calculation(self) -> None:
        """New cursor position equals old position plus inserted length."""
        result = insert_text_at_cursor("abc", 1, "XYZ")
        assert result == ("aXYZbc", 4)

    def test_negative_cursor_raises_valueerror(self) -> None:
        """Negative cursor_index raises ValueError."""
        with pytest.raises(ValueError):
            insert_text_at_cursor("hello", -1, "x")

    def test_cursor_beyond_length_raises_valueerror(self) -> None:
        """cursor_index > len(current_text) raises ValueError."""
        with pytest.raises(ValueError):
            insert_text_at_cursor("hello", 6, "x")


class TestHandlePaste:
    """Tests for handle_paste function."""

    def test_normal_paste_returns_new_text_and_cursor(self) -> None:
        """Normal paste returns tuple with new text and cursor."""
        result = handle_paste("hello", 5, "world")
        assert result == ("helloworld", 10)

    def test_empty_paste_content_returns_none(self) -> None:
        """Empty paste_content returns None."""
        assert handle_paste("hello", 3, "") is None

    def test_whitespace_only_paste_returns_none(self) -> None:
        """Whitespace-only paste_content returns None after strip."""
        assert handle_paste("hello", 3, "   ") is None

    def test_paste_strips_leading_trailing_whitespace(self) -> None:
        """Paste strips leading and trailing whitespace before insert."""
        result = handle_paste("ab", 1, "  X  ")
        assert result == ("aXb", 2)

    def test_multiline_paste_content_handled(self) -> None:
        """Multi-line paste content is handled correctly."""
        result = handle_paste("", 0, "  line1\nline2  ")
        assert result == ("line1\nline2", 11)
