#!/usr/bin/env python3
"""Tests for emacs-style yank operation (Ctrl+Y)."""

from platyplaty.ui.editing_mode import PromptState
from platyplaty.ui.emacs_editing import EmacsEditingMode


class TestYankBasic:
    """Tests for basic Ctrl+Y yank behavior."""

    def test_ctrl_y_inserts_yank_buffer_at_cursor(self) -> None:
        """Ctrl+Y inserts yank buffer contents at cursor position."""
        mode = EmacsEditingMode()
        mode._yank_buffer = "inserted"
        state = PromptState("hello world", 6)
        result = mode.handle_key("ctrl+y", None, state)
        assert result is not None
        assert result.new_text == "hello insertedworld"
        assert result.state_changed is True

    def test_ctrl_y_moves_cursor_past_inserted_text(self) -> None:
        """Ctrl+Y moves cursor to end of inserted text."""
        mode = EmacsEditingMode()
        mode._yank_buffer = "abc"
        state = PromptState("hello", 2)
        result = mode.handle_key("ctrl+y", None, state)
        assert result is not None
        assert result.new_cursor == 5  # 2 + len("abc")
        assert result.new_text == "heabcllo"

    def test_ctrl_y_empty_buffer_is_noop(self) -> None:
        """Ctrl+Y with empty buffer is no-op with state_changed False."""
        mode = EmacsEditingMode()
        state = PromptState("hello", 3)
        result = mode.handle_key("ctrl+y", None, state)
        assert result is not None
        assert result.new_text == "hello"
        assert result.new_cursor == 3
        assert result.state_changed is False

    def test_ctrl_y_resets_last_was_cut(self) -> None:
        """Ctrl+Y resets last_was_cut flag to break cut chain."""
        mode = EmacsEditingMode()
        mode._last_was_cut = True
        mode._yank_buffer = "text"
        state = PromptState("hello", 0)
        mode.handle_key("ctrl+y", None, state)
        assert mode._last_was_cut is False

    def test_ctrl_y_empty_buffer_still_resets_last_was_cut(self) -> None:
        """Ctrl+Y with empty buffer still resets last_was_cut flag."""
        mode = EmacsEditingMode()
        mode._last_was_cut = True
        state = PromptState("hello", 0)
        mode.handle_key("ctrl+y", None, state)
        assert mode._last_was_cut is False

    def test_ctrl_y_at_start_of_text(self) -> None:
        """Ctrl+Y at start inserts at beginning."""
        mode = EmacsEditingMode()
        mode._yank_buffer = "prefix"
        state = PromptState("hello", 0)
        result = mode.handle_key("ctrl+y", None, state)
        assert result is not None
        assert result.new_text == "prefixhello"
        assert result.new_cursor == 6

    def test_ctrl_y_at_end_of_text(self) -> None:
        """Ctrl+Y at end appends to text."""
        mode = EmacsEditingMode()
        mode._yank_buffer = "suffix"
        state = PromptState("hello", 5)
        result = mode.handle_key("ctrl+y", None, state)
        assert result is not None
        assert result.new_text == "hellosuffix"
        assert result.new_cursor == 11

    def test_ctrl_y_into_empty_text(self) -> None:
        """Ctrl+Y into empty text works correctly."""
        mode = EmacsEditingMode()
        mode._yank_buffer = "content"
        state = PromptState("", 0)
        result = mode.handle_key("ctrl+y", None, state)
        assert result is not None
        assert result.new_text == "content"
        assert result.new_cursor == 7


class TestYankAfterCut:
    """Tests for yank after cut operations."""

    def test_ctrl_k_then_ctrl_y_restores_text(self) -> None:
        """Ctrl+K followed by Ctrl+Y restores the cut text."""
        mode = EmacsEditingMode()
        state = PromptState("hello world", 6)
        result = mode.handle_key("ctrl+k", None, state)
        assert result is not None
        # Now yank at the same position
        state2 = PromptState(result.new_text, result.new_cursor)
        result2 = mode.handle_key("ctrl+y", None, state2)
        assert result2 is not None
        assert result2.new_text == "hello world"

    def test_cursor_position_correct_after_yank(self) -> None:
        """Cursor is at end of yanked text after Ctrl+Y."""
        mode = EmacsEditingMode()
        state = PromptState("hello world", 6)
        result = mode.handle_key("ctrl+k", None, state)
        assert result is not None
        state2 = PromptState(result.new_text, result.new_cursor)
        result2 = mode.handle_key("ctrl+y", None, state2)
        assert result2 is not None
        assert result2.new_cursor == 11  # 6 + len("world")

    def test_ctrl_u_then_ctrl_y_at_different_position(self) -> None:
        """Cut from beginning, then yank at different position."""
        mode = EmacsEditingMode()
        state = PromptState("hello world", 6)
        result = mode.handle_key("ctrl+u", None, state)
        assert result is not None
        assert result.new_text == "world"
        # Yank at end of remaining text
        state2 = PromptState(result.new_text, 5)
        result2 = mode.handle_key("ctrl+y", None, state2)
        assert result2 is not None
        assert result2.new_text == "worldhello "
        assert result2.new_cursor == 11


class TestYankBufferPersistence:
    """Tests for yank buffer persistence across prompt invocations."""

    def test_yank_buffer_persists_across_reset_transient_state(self) -> None:
        """Yank buffer is not cleared by reset_transient_state."""
        mode = EmacsEditingMode()
        # Cut some text
        state = PromptState("hello world", 6)
        mode.handle_key("ctrl+k", None, state)
        assert mode.yank_buffer == "world"
        # Simulate prompt reopen
        mode.reset_transient_state()
        # Yank should still work with previously cut text
        state2 = PromptState("new text", 4)
        result = mode.handle_key("ctrl+y", None, state2)
        assert result is not None
        assert result.new_text == "new worldtext"
        assert mode.yank_buffer == "world"
