#!/usr/bin/env python3
"""Unit tests for command prompt horizontal scrolling logic."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.command_prompt import CommandPrompt


class MockSize:
    """Mock for Textual widget size."""

    def __init__(self, width: int, height: int = 1):
        self.width = width
        self.height = height


class TestUpdateCursorWithScroll:
    """Tests for scroll offset calculation."""

    def make_prompt(self, width: int, text: str = "", scroll: int = 0):
        """Create a mock prompt with given width and state."""
        prompt = MagicMock(spec=CommandPrompt)
        prompt.size = MockSize(width)
        prompt._text_scroll = scroll
        prompt.cursor_index = 0
        prompt.input_text = text
        prompt.update_cursor_with_scroll = (
            CommandPrompt.update_cursor_with_scroll.__get__(prompt, CommandPrompt)
        )
        return prompt

    def test_cursor_within_visible_area_no_scroll(self):
        """Cursor within visible width doesn't change scroll offset."""
        prompt = self.make_prompt(width=20, text="hello")
        prompt.update_cursor_with_scroll(3)
        assert prompt._text_scroll == 0
        assert prompt.cursor_index == 3

    def test_cursor_moves_past_right_edge_scrolls(self):
        """Cursor moving past right edge increases scroll offset."""
        prompt = self.make_prompt(width=10, text="0123456789abcdef")
        # visible_width = 10 - 1 = 9
        # If cursor is at position 10, it's past visible_width-1 = 8
        prompt.update_cursor_with_scroll(10)
        # _text_scroll = 10 - 9 + 1 = 2
        assert prompt._text_scroll == 2
        assert prompt.cursor_index == 10

    def test_cursor_moves_left_of__text_scroll_scrolls_left(self):
        """Cursor moving left of scroll offset decreases scroll offset."""
        prompt = self.make_prompt(width=10, text="0123456789", scroll=5)
        prompt.update_cursor_with_scroll(3)
        assert prompt._text_scroll == 3
        assert prompt.cursor_index == 3

    def test_eol_cursor_scrolls_to_show_space(self):
        """Cursor at end of text scrolls to show the EOL space."""
        prompt = self.make_prompt(width=10, text="0123456789abcdef")
        # visible_width = 9, text len = 16, cursor at 16 (EOL)
        # _text_scroll = 16 - 9 + 1 = 8
        prompt.update_cursor_with_scroll(16)
        assert prompt._text_scroll == 8
        assert prompt.cursor_index == 16

    def test_narrow_width_handled(self):
        """Very narrow width (visible_width < 1) is handled."""
        prompt = self.make_prompt(width=1, text="abc")
        # visible_width = max(1, 1-1) = 1 (clamped)
        prompt.update_cursor_with_scroll(2)
        # _text_scroll should be adjusted so cursor is visible
        assert prompt.cursor_index == 2


class TestOnResize:
    """Tests for scroll adjustment on resize."""

    def make_prompt(self, width: int, text: str, cursor: int, scroll: int):
        """Create a mock prompt for resize testing."""
        prompt = MagicMock(spec=CommandPrompt)
        prompt.size = MockSize(width)
        prompt._text_scroll = scroll
        prompt.cursor_index = cursor
        prompt.input_text = text
        prompt.on_resize = CommandPrompt.on_resize.__get__(prompt, CommandPrompt)
        return prompt

    def test_resize_wider_keeps_cursor_visible(self):
        """Resizing wider keeps cursor visible."""
        prompt = self.make_prompt(width=20, text="abc", cursor=2, scroll=0)
        prompt.on_resize(None)
        assert prompt._text_scroll == 0

    def test_resize_narrower_adjusts_scroll(self):
        """Resizing narrower adjusts scroll to keep cursor visible."""
        prompt = self.make_prompt(
            width=5, text="0123456789", cursor=8, scroll=0
        )
        # visible_width = 4, cursor at 8, scroll at 0
        # cursor > scroll + visible_width - 1 = 0 + 4 - 1 = 3
        # So _text_scroll = 8 - 4 + 1 = 5
        prompt.on_resize(None)
        assert prompt._text_scroll == 5
