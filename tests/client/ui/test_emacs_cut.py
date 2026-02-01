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


class TestCutWord:
    """Tests for Ctrl+W (cut previous word) and Alt+D (cut word forward)."""

    def test_ctrl_w_cuts_previous_word(self) -> None:
        """Ctrl+W cuts the previous word."""
        mode = EmacsEditingMode()
        state = PromptState("hello world", 11)
        result = mode.handle_key("ctrl+w", None, state)
        assert result is not None
        assert result.new_text == "hello "
        assert result.new_cursor == 6
        assert result.state_changed is True

    def test_ctrl_w_stores_in_yank_buffer(self) -> None:
        """Ctrl+W stores cut text in yank buffer."""
        mode = EmacsEditingMode()
        state = PromptState("hello world", 11)
        mode.handle_key("ctrl+w", None, state)
        assert mode.yank_buffer == "world"

    def test_ctrl_w_at_start_is_noop(self) -> None:
        """Ctrl+W at start of line is no-op with state_changed False."""
        mode = EmacsEditingMode()
        state = PromptState("hello", 0)
        result = mode.handle_key("ctrl+w", None, state)
        assert result is not None
        assert result.new_text == "hello"
        assert result.new_cursor == 0
        assert result.state_changed is False

    def test_ctrl_w_unix_word_includes_slashes(self) -> None:
        """Ctrl+W treats slashes as part of the word (unix word definition)."""
        mode = EmacsEditingMode()
        state = PromptState("xyz foo/bar/baz.milk", 20)
        result = mode.handle_key("ctrl+w", None, state)
        assert result is not None
        assert result.new_text == "xyz "
        assert result.new_cursor == 4
        assert mode.yank_buffer == "foo/bar/baz.milk"

    def test_ctrl_w_unix_word_includes_hyphens_underscores_dots(self) -> None:
        """Ctrl+W treats hyphens, underscores, dots as part of word."""
        mode = EmacsEditingMode()
        state = PromptState("path my-file_name.txt", 21)
        result = mode.handle_key("ctrl+w", None, state)
        assert result is not None
        assert result.new_text == "path "
        assert mode.yank_buffer == "my-file_name.txt"

    def test_ctrl_w_sets_last_was_cut(self) -> None:
        """Ctrl+W sets last_was_cut flag for consecutive append."""
        mode = EmacsEditingMode()
        state = PromptState("hello world", 11)
        mode.handle_key("ctrl+w", None, state)
        assert mode._last_was_cut is True

    def test_ctrl_w_noop_preserves_cut_chain(self) -> None:
        """No-op Ctrl+W does not modify last_was_cut flag."""
        mode = EmacsEditingMode()
        mode._last_was_cut = True
        state = PromptState("hello", 0)
        mode.handle_key("ctrl+w", None, state)
        assert mode._last_was_cut is True

    def test_alt_d_cuts_word_forward(self) -> None:
        """Alt+D cuts word forward from cursor."""
        mode = EmacsEditingMode()
        state = PromptState("hello world", 0)
        result = mode.handle_key("alt+d", None, state)
        assert result is not None
        assert result.new_text == " world"
        assert result.new_cursor == 0
        assert result.state_changed is True

    def test_alt_d_stores_in_yank_buffer(self) -> None:
        """Alt+D stores cut text in yank buffer."""
        mode = EmacsEditingMode()
        state = PromptState("hello world", 0)
        mode.handle_key("alt+d", None, state)
        assert mode.yank_buffer == "hello"

    def test_alt_d_at_end_is_noop(self) -> None:
        """Alt+D at end of line is no-op with state_changed False."""
        mode = EmacsEditingMode()
        state = PromptState("hello", 5)
        result = mode.handle_key("alt+d", None, state)
        assert result is not None
        assert result.new_text == "hello"
        assert result.new_cursor == 5
        assert result.state_changed is False

    def test_alt_d_alphanumeric_boundary(self) -> None:
        """Alt+D uses alphanumeric word boundaries (punctuation is boundary)."""
        mode = EmacsEditingMode()
        state = PromptState("foo-bar baz", 0)
        result = mode.handle_key("alt+d", None, state)
        assert result is not None
        # Only "foo" is cut, hyphen is a boundary
        assert result.new_text == "-bar baz"
        assert mode.yank_buffer == "foo"

    def test_alt_d_sets_last_was_cut(self) -> None:
        """Alt+D sets last_was_cut flag for consecutive append."""
        mode = EmacsEditingMode()
        state = PromptState("hello world", 0)
        mode.handle_key("alt+d", None, state)
        assert mode._last_was_cut is True

    def test_alt_d_noop_preserves_cut_chain(self) -> None:
        """No-op Alt+D does not modify last_was_cut flag."""
        mode = EmacsEditingMode()
        mode._last_was_cut = True
        state = PromptState("hello", 5)
        mode.handle_key("alt+d", None, state)
        assert mode._last_was_cut is True

    def test_escape_d_works_same_as_alt_d(self) -> None:
        """escape+d is equivalent to alt+d for terminal compatibility."""
        mode = EmacsEditingMode()
        state = PromptState("hello world", 0)
        result = mode.handle_key("escape+d", None, state)
        assert result is not None
        assert result.new_text == " world"
        assert mode.yank_buffer == "hello"
