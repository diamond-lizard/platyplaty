#!/usr/bin/env python3
"""Tests for emacs-style cursor movement keybindings.

Tests Ctrl+A, Ctrl+E, Ctrl+B, Ctrl+F for single-character and
line-boundary cursor movement in EmacsEditingMode.
"""

from platyplaty.ui.editing_mode import PromptState
from platyplaty.ui.emacs_editing import EmacsEditingMode


class TestCursorMovementSingleChar:
    """Tests for single-character cursor movement (Ctrl+A/E/B/F)."""

    def test_ctrl_a_moves_to_start(self) -> None:
        """Ctrl+A moves cursor to beginning of line."""
        mode = EmacsEditingMode()
        state = PromptState("hello", 3)
        result = mode.handle_key("ctrl+a", None, state)
        assert result is not None
        assert result.new_cursor == 0
        assert result.new_text == "hello"
        assert result.state_changed is True

    def test_ctrl_a_at_start_returns_false(self) -> None:
        """Ctrl+A at start returns state_changed False."""
        mode = EmacsEditingMode()
        state = PromptState("hello", 0)
        result = mode.handle_key("ctrl+a", None, state)
        assert result is not None
        assert result.new_cursor == 0
        assert result.state_changed is False

    def test_ctrl_a_resets_last_was_cut(self) -> None:
        """Ctrl+A resets last_was_cut flag even when no-op (REQ-1900)."""
        mode = EmacsEditingMode()
        mode._last_was_cut = True
        state = PromptState("hello", 0)
        mode.handle_key("ctrl+a", None, state)
        assert mode._last_was_cut is False

    def test_ctrl_e_moves_to_end(self) -> None:
        """Ctrl+E moves cursor to end of line."""
        mode = EmacsEditingMode()
        state = PromptState("hello", 2)
        result = mode.handle_key("ctrl+e", None, state)
        assert result is not None
        assert result.new_cursor == 5
        assert result.new_text == "hello"
        assert result.state_changed is True

    def test_ctrl_e_at_end_returns_false(self) -> None:
        """Ctrl+E at end returns state_changed False."""
        mode = EmacsEditingMode()
        state = PromptState("hello", 5)
        result = mode.handle_key("ctrl+e", None, state)
        assert result is not None
        assert result.new_cursor == 5
        assert result.state_changed is False

    def test_ctrl_e_resets_last_was_cut(self) -> None:
        """Ctrl+E resets last_was_cut flag even when no-op (REQ-1900)."""
        mode = EmacsEditingMode()
        mode._last_was_cut = True
        state = PromptState("hello", 5)
        mode.handle_key("ctrl+e", None, state)
        assert mode._last_was_cut is False

    def test_ctrl_b_moves_back_one(self) -> None:
        """Ctrl+B moves cursor back one character."""
        mode = EmacsEditingMode()
        state = PromptState("hello", 3)
        result = mode.handle_key("ctrl+b", None, state)
        assert result is not None
        assert result.new_cursor == 2
        assert result.new_text == "hello"
        assert result.state_changed is True

    def test_ctrl_b_at_start_is_noop(self) -> None:
        """Ctrl+B at start is no-op with state_changed False."""
        mode = EmacsEditingMode()
        state = PromptState("hello", 0)
        result = mode.handle_key("ctrl+b", None, state)
        assert result is not None
        assert result.new_cursor == 0
        assert result.state_changed is False

    def test_ctrl_b_resets_last_was_cut(self) -> None:
        """Ctrl+B resets last_was_cut flag even when no-op (REQ-1900)."""
        mode = EmacsEditingMode()
        mode._last_was_cut = True
        state = PromptState("hello", 0)
        mode.handle_key("ctrl+b", None, state)
        assert mode._last_was_cut is False

    def test_ctrl_f_moves_forward_one(self) -> None:
        """Ctrl+F moves cursor forward one character."""
        mode = EmacsEditingMode()
        state = PromptState("hello", 2)
        result = mode.handle_key("ctrl+f", None, state)
        assert result is not None
        assert result.new_cursor == 3
        assert result.new_text == "hello"
        assert result.state_changed is True

    def test_ctrl_f_at_end_is_noop(self) -> None:
        """Ctrl+F at end is no-op with state_changed False."""
        mode = EmacsEditingMode()
        state = PromptState("hello", 5)
        result = mode.handle_key("ctrl+f", None, state)
        assert result is not None
        assert result.new_cursor == 5
        assert result.state_changed is False

    def test_ctrl_f_resets_last_was_cut(self) -> None:
        """Ctrl+F resets last_was_cut flag even when no-op (REQ-1900)."""
        mode = EmacsEditingMode()
        mode._last_was_cut = True
        state = PromptState("hello", 5)
        mode.handle_key("ctrl+f", None, state)
        assert mode._last_was_cut is False
