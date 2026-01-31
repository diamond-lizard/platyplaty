#!/usr/bin/env python3
"""Unit tests for command prompt paste functionality."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.command_prompt import CommandPrompt


@pytest.fixture
def mock_prompt():
    """Create a mock CommandPrompt with paste support."""
    prompt = MagicMock(spec=CommandPrompt)
    prompt.input_text = ""
    prompt.cursor_index = 0
    prompt.update_cursor_with_scroll = MagicMock()
    prompt.start_blink_timer = MagicMock()
    prompt.paste_text = CommandPrompt.paste_text.__get__(prompt, CommandPrompt)
    prompt.paste_from_selection = CommandPrompt.paste_from_selection.__get__(
        prompt, CommandPrompt
    )
    prompt.on_paste = CommandPrompt.on_paste.__get__(prompt, CommandPrompt)
    return prompt


class TestPasteText:
    """Tests for paste_text method."""

    def test_normal_paste_inserts_and_returns_true(self, mock_prompt):
        """Normal paste inserts text at cursor and returns True."""
        mock_prompt.input_text = "hello"
        mock_prompt.cursor_index = 5
        result = mock_prompt.paste_text("world")
        assert result is True
        assert mock_prompt.input_text == "helloworld"

    def test_empty_paste_is_noop_returns_false(self, mock_prompt):
        """Empty paste_content is no-op and returns False."""
        mock_prompt.input_text = "hello"
        mock_prompt.cursor_index = 3
        result = mock_prompt.paste_text("")
        assert result is False
        assert mock_prompt.input_text == "hello"

    def test_whitespace_only_paste_is_noop_returns_false(self, mock_prompt):
        """Whitespace-only paste_content is no-op and returns False."""
        mock_prompt.input_text = "hello"
        mock_prompt.cursor_index = 3
        result = mock_prompt.paste_text("   \t\n  ")
        assert result is False
        assert mock_prompt.input_text == "hello"

    def test_paste_strips_whitespace(self, mock_prompt):
        """Paste strips leading and trailing whitespace."""
        mock_prompt.input_text = "ab"
        mock_prompt.cursor_index = 1
        result = mock_prompt.paste_text("  X  ")
        assert result is True
        assert mock_prompt.input_text == "aXb"

    def test_paste_updates_cursor(self, mock_prompt):
        """Paste updates cursor position correctly."""
        mock_prompt.input_text = "ab"
        mock_prompt.cursor_index = 1
        mock_prompt.paste_text("XYZ")
        mock_prompt.update_cursor_with_scroll.assert_called_once_with(4)

    def test_paste_restarts_blink_timer(self, mock_prompt):
        """Paste restarts blink timer on success."""
        mock_prompt.input_text = ""
        mock_prompt.cursor_index = 0
        mock_prompt.paste_text("hello")
        mock_prompt.start_blink_timer.assert_called_once()

    def test_paste_no_blink_on_empty(self, mock_prompt):
        """Paste does not restart blink timer when no text inserted."""
        mock_prompt.input_text = ""
        mock_prompt.cursor_index = 0
        mock_prompt.paste_text("")
        mock_prompt.start_blink_timer.assert_not_called()


class TestPasteFromSelection:
    """Tests for paste_from_selection method."""

    @patch("platyplaty.ui.command_prompt_paste.get_primary_selection")
    def test_calls_get_primary_selection(self, mock_get_sel, mock_prompt):
        """paste_from_selection calls get_primary_selection."""
        mock_get_sel.return_value = "selected text"
        mock_prompt.paste_from_selection()
        mock_get_sel.assert_called_once()

    @patch("platyplaty.ui.command_prompt_paste.get_primary_selection")
    def test_pastes_selection_content(self, mock_get_sel, mock_prompt):
        """paste_from_selection pastes the selection content."""
        mock_get_sel.return_value = "selected"
        mock_prompt.input_text = ""
        mock_prompt.cursor_index = 0
        result = mock_prompt.paste_from_selection()
        assert result is True
        assert mock_prompt.input_text == "selected"


class TestOnPaste:
    """Tests for on_paste event handler."""

    def test_calls_event_stop(self, mock_prompt):
        """on_paste calls event.stop()."""
        event = MagicMock()
        event.text = "pasted"
        mock_prompt.on_paste(event)
        event.stop.assert_called_once()

    def test_pastes_event_text(self, mock_prompt):
        """on_paste pastes event.text content."""
        event = MagicMock()
        event.text = "pasted"
        mock_prompt.input_text = ""
        mock_prompt.cursor_index = 0
        mock_prompt.on_paste(event)
        assert mock_prompt.input_text == "pasted"
