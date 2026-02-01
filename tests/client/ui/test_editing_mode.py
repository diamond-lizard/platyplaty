#!/usr/bin/env python3
"""Tests for editing mode Protocol and dataclasses.

This module tests the EditResult and PromptState dataclasses
defined in the editing_mode module.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.editing_mode import EditResult, PromptState


class TestPromptState:
    """Tests for PromptState dataclass."""

    def test_fields_are_accessible(self) -> None:
        """PromptState fields can be accessed."""
        state = PromptState(text="hello", cursor=3)
        assert state.text == "hello"
        assert state.cursor == 3

    def test_empty_text(self) -> None:
        """PromptState works with empty text."""
        state = PromptState(text="", cursor=0)
        assert state.text == ""
        assert state.cursor == 0


class TestEditResult:
    """Tests for EditResult dataclass."""

    def test_fields_are_accessible(self) -> None:
        """EditResult fields can be accessed."""
        result = EditResult(new_text="world", new_cursor=5, state_changed=True)
        assert result.new_text == "world"
        assert result.new_cursor == 5
        assert result.state_changed is True

    def test_state_changed_false(self) -> None:
        """EditResult can indicate no state change."""
        result = EditResult(new_text="same", new_cursor=0, state_changed=False)
        assert result.state_changed is False


class TestCreateEditingMode:
    """Tests for create_editing_mode factory function."""

    def test_returns_editing_mode_protocol(self) -> None:
        """create_editing_mode returns an object conforming to EditingMode."""
        from platyplaty.ui.editing_mode import EditingMode, create_editing_mode

        mode = create_editing_mode()
        # Verify it has the required methods
        assert hasattr(mode, "handle_key")
        assert hasattr(mode, "reset_transient_state")
        assert hasattr(mode, "reset_cut_chain")
        assert callable(mode.handle_key)
        assert callable(mode.reset_transient_state)
        assert callable(mode.reset_cut_chain)


class TestEmacsEditingMode:
    """Tests for EmacsEditingMode class."""

    def test_yank_buffer_starts_empty(self) -> None:
        """Yank buffer is empty on initialization."""
        from platyplaty.ui.emacs_editing import EmacsEditingMode

        mode = EmacsEditingMode()
        assert mode.yank_buffer == ""

    def test_reset_transient_state_preserves_yank_buffer(self) -> None:
        """reset_transient_state does not clear the yank buffer."""
        from platyplaty.ui.emacs_editing import EmacsEditingMode

        mode = EmacsEditingMode()
        mode._yank_buffer = "some text"
        mode.reset_transient_state()
        assert mode.yank_buffer == "some text"

    def test_handle_key_returns_none_for_unhandled(self) -> None:
        """handle_key returns None for unhandled keys."""
        from platyplaty.ui.emacs_editing import EmacsEditingMode

        mode = EmacsEditingMode()
        state = PromptState(text="hello", cursor=0)
        result = mode.handle_key("x", "x", state)
        assert result is None

    def test_reset_cut_chain_clears_last_was_cut(self) -> None:
        """reset_cut_chain sets _last_was_cut to False."""
        from platyplaty.ui.emacs_editing import EmacsEditingMode

        mode = EmacsEditingMode()
        mode._last_was_cut = True
        mode.reset_cut_chain()
        assert mode._last_was_cut is False
