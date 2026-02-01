#!/usr/bin/env python3
"""Tests for emacs-style cut operations (Ctrl+K, Ctrl+U)."""

import pytest

from platyplaty.ui.editing_mode import PromptState
from platyplaty.ui.emacs_editing import EmacsEditingMode


class TestCutToLineBoundary:
    """Tests for Ctrl+K (cut to end) and Ctrl+U (cut to beginning)."""

    def test_ctrl_k_cuts_to_end(self) -> None:
        """Ctrl+K cuts text from cursor to end of line."""
        mode = EmacsEditingMode()
        state = PromptState("hello world", 6)
        result = mode.handle_key("ctrl+k", None, state)
        assert result is not None
        assert result.new_text == "hello "
        assert result.new_cursor == 6
        assert result.state_changed is True

    def test_ctrl_k_stores_in_yank_buffer(self) -> None:
        """Ctrl+K stores cut text in yank buffer."""
        mode = EmacsEditingMode()
        state = PromptState("hello world", 6)
        mode.handle_key("ctrl+k", None, state)
        assert mode.yank_buffer == "world"

    def test_ctrl_k_at_end_is_noop(self) -> None:
        """Ctrl+K at end of line is no-op with state_changed False."""
        mode = EmacsEditingMode()
        state = PromptState("hello", 5)
        result = mode.handle_key("ctrl+k", None, state)
        assert result is not None
        assert result.new_text == "hello"
        assert result.new_cursor == 5
        assert result.state_changed is False

    def test_ctrl_k_sets_last_was_cut(self) -> None:
        """Ctrl+K sets last_was_cut flag for consecutive append."""
        mode = EmacsEditingMode()
        state = PromptState("hello world", 6)
        mode.handle_key("ctrl+k", None, state)
        assert mode._last_was_cut is True

    def test_ctrl_k_noop_preserves_cut_chain(self) -> None:
        """No-op Ctrl+K does not modify last_was_cut flag."""
        mode = EmacsEditingMode()
        mode._last_was_cut = True
        state = PromptState("hello", 5)
        mode.handle_key("ctrl+k", None, state)
        assert mode._last_was_cut is True

    def test_ctrl_u_cuts_to_beginning(self) -> None:
        """Ctrl+U cuts text from beginning to cursor."""
        mode = EmacsEditingMode()
        state = PromptState("hello world", 6)
        result = mode.handle_key("ctrl+u", None, state)
        assert result is not None
        assert result.new_text == "world"
        assert result.new_cursor == 0
        assert result.state_changed is True

    def test_ctrl_u_stores_in_yank_buffer(self) -> None:
        """Ctrl+U stores cut text in yank buffer."""
        mode = EmacsEditingMode()
        state = PromptState("hello world", 6)
        mode.handle_key("ctrl+u", None, state)
        assert mode.yank_buffer == "hello "

    def test_ctrl_u_at_start_is_noop(self) -> None:
        """Ctrl+U at start of line is no-op with state_changed False."""
        mode = EmacsEditingMode()
        state = PromptState("hello", 0)
        result = mode.handle_key("ctrl+u", None, state)
        assert result is not None
        assert result.new_text == "hello"
        assert result.new_cursor == 0
        assert result.state_changed is False

    def test_ctrl_u_sets_last_was_cut(self) -> None:
        """Ctrl+U sets last_was_cut flag for consecutive append."""
        mode = EmacsEditingMode()
        state = PromptState("hello world", 6)
        mode.handle_key("ctrl+u", None, state)
        assert mode._last_was_cut is True

    def test_ctrl_u_noop_preserves_cut_chain(self) -> None:
        """No-op Ctrl+U does not modify last_was_cut flag."""
        mode = EmacsEditingMode()
        mode._last_was_cut = True
        state = PromptState("hello", 0)
        mode.handle_key("ctrl+u", None, state)
        assert mode._last_was_cut is True
