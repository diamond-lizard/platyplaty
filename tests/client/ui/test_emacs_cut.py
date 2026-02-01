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


class TestConsecutiveCutAppend:
    """Tests for consecutive cut commands appending to yank buffer."""

    def test_consecutive_ctrl_k_appends(self) -> None:
        """Two consecutive Ctrl+K calls append to yank buffer."""
        mode = EmacsEditingMode()
        # First cut: "world" from "hello world"
        state1 = PromptState("hello world", 6)
        mode.handle_key("ctrl+k", None, state1)
        assert mode.yank_buffer == "world"
        # Second cut: "hello" from remaining "hello "
        state2 = PromptState("hello ", 0)
        mode.handle_key("ctrl+k", None, state2)
        assert mode.yank_buffer == "worldhello "

    def test_ctrl_k_then_ctrl_u_appends(self) -> None:
        """Ctrl+K followed by Ctrl+U appends to yank buffer."""
        mode = EmacsEditingMode()
        # Ctrl+K cuts "world"
        state1 = PromptState("hello world", 6)
        mode.handle_key("ctrl+k", None, state1)
        assert mode.yank_buffer == "world"
        # Ctrl+U cuts "hello " (from remaining "hello ")
        state2 = PromptState("hello ", 6)
        mode.handle_key("ctrl+u", None, state2)
        assert mode.yank_buffer == "worldhello "

    def test_mixed_cut_commands_append(self) -> None:
        """Mixing different cut commands (Ctrl+W, Alt+D) appends."""
        mode = EmacsEditingMode()
        # Alt+D cuts "foo"
        state1 = PromptState("foo bar baz", 0)
        mode.handle_key("alt+d", None, state1)
        assert mode.yank_buffer == "foo"
        # Ctrl+W cuts "bar" (from remaining " bar baz", cursor at end)
        state2 = PromptState(" bar baz", 8)
        mode.handle_key("ctrl+w", None, state2)
        assert mode.yank_buffer == "foobaz"

    def test_cursor_move_breaks_chain(self) -> None:
        """Ctrl+K then cursor move then Ctrl+K replaces buffer."""
        mode = EmacsEditingMode()
        # First cut
        state1 = PromptState("hello world", 6)
        mode.handle_key("ctrl+k", None, state1)
        assert mode.yank_buffer == "world"
        # Cursor move (Ctrl+B) breaks chain
        state2 = PromptState("hello ", 6)
        mode.handle_key("ctrl+b", None, state2)
        # Second cut replaces (not appends)
        state3 = PromptState("hello ", 5)
        mode.handle_key("ctrl+k", None, state3)
        assert mode.yank_buffer == " "

    def test_char_insert_breaks_chain(self) -> None:
        """Ctrl+K then character insert then Ctrl+K replaces buffer."""
        mode = EmacsEditingMode()
        # First cut
        state1 = PromptState("hello world", 6)
        mode.handle_key("ctrl+k", None, state1)
        assert mode.yank_buffer == "world"
        # Character insert breaks chain (simulate by calling reset_cut_chain)
        mode.reset_cut_chain()
        # Second cut replaces (not appends)
        state2 = PromptState("hello X", 6)
        mode.handle_key("ctrl+k", None, state2)
        assert mode.yank_buffer == "X"


    def test_noop_cut_preserves_chain(self) -> None:
        """No-op Ctrl+K preserves chain: subsequent cut appends.
        
        Starting with text "worldhello" and cursor at position 5:
        - Ctrl+K cuts "hello" (from cursor to end), text becomes "world"
        - Ctrl+K (no-op since nothing after cursor)
        - Ctrl+U cuts "world" (from start to cursor)
        Verify yank buffer contains "helloworld" (appended, not replaced).
        """
        mode = EmacsEditingMode()
        # First cut: "hello" from position 5 to end
        state1 = PromptState("worldhello", 5)
        mode.handle_key("ctrl+k", None, state1)
        assert mode.yank_buffer == "hello"
        assert mode._last_was_cut is True
        # No-op Ctrl+K (cursor at end, nothing to cut)
        state2 = PromptState("world", 5)
        result = mode.handle_key("ctrl+k", None, state2)
        assert result is not None
        assert result.state_changed is False
        assert mode._last_was_cut is True  # Chain preserved
        # Ctrl+U cuts "world"
        state3 = PromptState("world", 5)
        mode.handle_key("ctrl+u", None, state3)
        assert mode.yank_buffer == "helloworld"

    def test_noop_non_cut_breaks_chain(self) -> None:
        """No-op non-cut command (Ctrl+F at end) breaks chain.
        
        Starting with text "ab" and cursor at position 1:
        - Ctrl+K cuts "b" (yank buffer = "b", last_was_cut = True)
        - Ctrl+F (no-op since cursor is already at end of text after cut)
        - Ctrl+A moves cursor to 0
        - Ctrl+K cuts "a"
        Verify yank buffer contains only "a" (replaced, not appended).
        """
        mode = EmacsEditingMode()
        # First cut: "b" from position 1
        state1 = PromptState("ab", 1)
        mode.handle_key("ctrl+k", None, state1)
        assert mode.yank_buffer == "b"
        assert mode._last_was_cut is True
        # No-op Ctrl+F (cursor already at end after cut)
        state2 = PromptState("a", 1)
        result = mode.handle_key("ctrl+f", None, state2)
        assert result is not None
        assert result.state_changed is False
        assert mode._last_was_cut is False  # Chain broken by non-cut
        # Ctrl+A moves to start
        state3 = PromptState("a", 1)
        mode.handle_key("ctrl+a", None, state3)
        # Second cut replaces (not appends)
        state4 = PromptState("a", 0)
        mode.handle_key("ctrl+k", None, state4)
        assert mode.yank_buffer == "a"

    def test_reset_transient_state_clears_last_was_cut(self) -> None:
        """reset_transient_state clears last_was_cut, causing next cut to replace."""
        mode = EmacsEditingMode()
        # First cut
        state1 = PromptState("hello world", 6)
        mode.handle_key("ctrl+k", None, state1)
        assert mode.yank_buffer == "world"
        assert mode._last_was_cut is True
        # Simulate prompt close/reopen
        mode.reset_transient_state()
        assert mode._last_was_cut is False
        # Second cut replaces (not appends) due to reset
        state2 = PromptState("foo bar", 4)
        mode.handle_key("ctrl+k", None, state2)
        assert mode.yank_buffer == "bar"
