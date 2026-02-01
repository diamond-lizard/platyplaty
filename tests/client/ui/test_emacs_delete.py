#!/usr/bin/env python3
"""Tests for emacs-style delete keybinding.

Tests Ctrl+D for deleting character at cursor position in EmacsEditingMode.
"""

from platyplaty.ui.editing_mode import PromptState
from platyplaty.ui.emacs_editing import EmacsEditingMode


class TestDeleteCharacter:
    """Tests for Ctrl+D delete character at cursor."""

    def test_ctrl_d_deletes_at_cursor(self) -> None:
        """Ctrl+D deletes character at cursor position."""
        mode = EmacsEditingMode()
        state = PromptState("hello", 2)
        result = mode.handle_key("ctrl+d", None, state)
        assert result is not None
        assert result.new_text == "helo"
        assert result.new_cursor == 2
        assert result.state_changed is True

    def test_ctrl_d_at_end_is_noop(self) -> None:
        """Ctrl+D at end of text is no-op with state_changed False."""
        mode = EmacsEditingMode()
        state = PromptState("hello", 5)
        result = mode.handle_key("ctrl+d", None, state)
        assert result is not None
        assert result.new_text == "hello"
        assert result.new_cursor == 5
        assert result.state_changed is False

    def test_ctrl_d_cursor_unchanged(self) -> None:
        """Ctrl+D keeps cursor position after delete."""
        mode = EmacsEditingMode()
        state = PromptState("abcde", 0)
        result = mode.handle_key("ctrl+d", None, state)
        assert result is not None
        assert result.new_text == "bcde"
        assert result.new_cursor == 0

    def test_ctrl_d_resets_last_was_cut(self) -> None:
        """Ctrl+D resets last_was_cut flag."""
        mode = EmacsEditingMode()
        mode._last_was_cut = True
        state = PromptState("hello", 2)
        mode.handle_key("ctrl+d", None, state)
        assert mode._last_was_cut is False

    def test_ctrl_d_noop_resets_last_was_cut(self) -> None:
        """Ctrl+D at end still resets last_was_cut flag."""
        mode = EmacsEditingMode()
        mode._last_was_cut = True
        state = PromptState("hello", 5)
        mode.handle_key("ctrl+d", None, state)
        assert mode._last_was_cut is False

    def test_ctrl_d_empty_text_is_noop(self) -> None:
        """Ctrl+D on empty text is no-op."""
        mode = EmacsEditingMode()
        state = PromptState("", 0)
        result = mode.handle_key("ctrl+d", None, state)
        assert result is not None
        assert result.new_text == ""
        assert result.new_cursor == 0
        assert result.state_changed is False

    def test_ctrl_d_deletes_last_char(self) -> None:
        """Ctrl+D deletes last character when cursor before it."""
        mode = EmacsEditingMode()
        state = PromptState("ab", 1)
        result = mode.handle_key("ctrl+d", None, state)
        assert result is not None
        assert result.new_text == "a"
        assert result.new_cursor == 1
        assert result.state_changed is True
