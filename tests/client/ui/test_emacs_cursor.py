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


class TestCursorMovementWord:
    """Tests for word-based cursor movement (Alt+B, Alt+F)."""

    def test_alt_b_moves_to_start_of_previous_word(self) -> None:
        """Alt+B moves cursor to start of previous word."""
        mode = EmacsEditingMode()
        state = PromptState("hello world", 11)
        result = mode.handle_key("alt+b", None, state)
        assert result is not None
        assert result.new_cursor == 6
        assert result.new_text == "hello world"
        assert result.state_changed is True

    def test_alt_b_skips_non_alphanumeric(self) -> None:
        """Alt+B skips non-alphanumeric characters between words."""
        mode = EmacsEditingMode()
        state = PromptState("hello   world", 13)
        result = mode.handle_key("alt+b", None, state)
        assert result is not None
        assert result.new_cursor == 8

    def test_alt_b_at_start_is_noop(self) -> None:
        """Alt+B at start is no-op with state_changed False."""
        mode = EmacsEditingMode()
        state = PromptState("hello", 0)
        result = mode.handle_key("alt+b", None, state)
        assert result is not None
        assert result.new_cursor == 0
        assert result.state_changed is False

    def test_alt_b_resets_last_was_cut(self) -> None:
        """Alt+B resets last_was_cut flag even when no-op (REQ-1900)."""
        mode = EmacsEditingMode()
        mode._last_was_cut = True
        state = PromptState("hello", 0)
        mode.handle_key("alt+b", None, state)
        assert mode._last_was_cut is False

    def test_escape_b_also_works(self) -> None:
        """escape+b works same as alt+b for terminal compatibility."""
        mode = EmacsEditingMode()
        state = PromptState("hello world", 11)
        result = mode.handle_key("escape+b", None, state)
        assert result is not None
        assert result.new_cursor == 6

    def test_alt_f_moves_to_end_of_next_word(self) -> None:
        """Alt+F moves cursor to end of next word."""
        mode = EmacsEditingMode()
        state = PromptState("hello world", 0)
        result = mode.handle_key("alt+f", None, state)
        assert result is not None
        assert result.new_cursor == 5
        assert result.new_text == "hello world"
        assert result.state_changed is True

    def test_alt_f_skips_non_alphanumeric(self) -> None:
        """Alt+F skips non-alphanumeric characters between words."""
        mode = EmacsEditingMode()
        state = PromptState("hello   world", 5)
        result = mode.handle_key("alt+f", None, state)
        assert result is not None
        assert result.new_cursor == 13

    def test_alt_f_at_end_is_noop(self) -> None:
        """Alt+F at end is no-op with state_changed False."""
        mode = EmacsEditingMode()
        state = PromptState("hello", 5)
        result = mode.handle_key("alt+f", None, state)
        assert result is not None
        assert result.new_cursor == 5
        assert result.state_changed is False

    def test_alt_f_resets_last_was_cut(self) -> None:
        """Alt+F resets last_was_cut flag even when no-op (REQ-1900)."""
        mode = EmacsEditingMode()
        mode._last_was_cut = True
        state = PromptState("hello", 5)
        mode.handle_key("alt+f", None, state)
        assert mode._last_was_cut is False

    def test_escape_f_also_works(self) -> None:
        """escape+f works same as alt+f for terminal compatibility."""
        mode = EmacsEditingMode()
        state = PromptState("hello world", 0)
        result = mode.handle_key("escape+f", None, state)
        assert result is not None
        assert result.new_cursor == 5

    def test_alt_b_treats_hyphenated_as_one_component(self) -> None:
        """Alt+B treats 'foo-bar' as one path component (path-aware boundaries)."""
        mode = EmacsEditingMode()
        state = PromptState("foo-bar", 7)
        result = mode.handle_key("alt+b", None, state)
        assert result is not None
        assert result.new_cursor == 0  # Start of "foo-bar" (path component)

    def test_alt_f_treats_hyphenated_as_one_component(self) -> None:
        """Alt+F treats 'foo-bar' as one path component (path-aware boundaries)."""
        mode = EmacsEditingMode()
        state = PromptState("foo-bar", 0)
        result = mode.handle_key("alt+f", None, state)
        assert result is not None
        assert result.new_cursor == 7  # End of "foo-bar" (path component)

    def test_alt_b_navigates_path_word_by_word(self) -> None:
        """Alt+B navigates 'foo/bar/baz.milk' path component by component."""
        mode = EmacsEditingMode()
        # Start at end, should go to start of "baz.milk" (path component)
        state = PromptState("foo/bar/baz.milk", 16)
        result = mode.handle_key("alt+b", None, state)
        assert result is not None
        assert result.new_cursor == 8  # Start of "baz.milk" (path component)

    def test_alt_f_navigates_path_word_by_word(self) -> None:
        """Alt+F navigates 'foo/bar/baz.milk' path component by component (path-aware boundaries)."""
        mode = EmacsEditingMode()
        # Start at beginning, should go past "foo/" (path component)
        state = PromptState("foo/bar/baz.milk", 0)
        result = mode.handle_key("alt+f", None, state)
        assert result is not None
        assert result.new_cursor == 4  # End of "foo/" (includes trailing slash)

    def test_alt_b_navigates_absolute_path(self) -> None:
        """Alt+B navigates through absolute path landing at component starts."""
        mode = EmacsEditingMode()
        # /foo/bar/baz from end (pos 12) -> 9 (start of baz)
        state = PromptState("/foo/bar/baz", 12)
        result = mode.handle_key("alt+b", None, state)
        assert result is not None
        assert result.new_cursor == 9  # Start of "baz"
        # Continue: 9 -> 5 (start of bar)
        state = PromptState("/foo/bar/baz", 9)
        result = mode.handle_key("alt+b", None, state)
        assert result.new_cursor == 5  # Start of "bar"
        # Continue: 5 -> 1 (start of foo)
        state = PromptState("/foo/bar/baz", 5)
        result = mode.handle_key("alt+b", None, state)
        assert result.new_cursor == 1  # Start of "foo"
        # Continue: 1 -> 0 (leading slash)
        state = PromptState("/foo/bar/baz", 1)
        result = mode.handle_key("alt+b", None, state)
        assert result.new_cursor == 0  # Leading slash

    def test_alt_b_mixed_content_with_spaces(self) -> None:
        """Alt+B handles mixed content with spaces correctly."""
        mode = EmacsEditingMode()
        # "load /foo/bar" from end (pos 13) -> 10 (start of bar)
        state = PromptState("load /foo/bar", 13)
        result = mode.handle_key("alt+b", None, state)
        assert result is not None
        assert result.new_cursor == 10  # Start of "bar"
        # Continue: 10 -> 6 (start of foo)
        state = PromptState("load /foo/bar", 10)
        result = mode.handle_key("alt+b", None, state)
        assert result.new_cursor == 6  # Start of "foo"
        # Continue: 6 -> 0 (start of load, skipping slash and space)
        state = PromptState("load /foo/bar", 6)
        result = mode.handle_key("alt+b", None, state)
        assert result.new_cursor == 0  # Start of "load"

    def test_alt_f_navigates_load_command_with_path(self) -> None:
        """Alt+F navigates 'load /foo/bar' absorbing lone slash after word."""
        mode = EmacsEditingMode()
        # Start at beginning, should go past "load /" (absorbs lone slash)
        state = PromptState("load /foo/bar", 0)
        result = mode.handle_key("alt+f", None, state)
        assert result is not None
        assert result.new_cursor == 6  # After "load /"
        # Continue: 6 -> 10 (after "foo/")
        state = PromptState("load /foo/bar", 6)
        result = mode.handle_key("alt+f", None, state)
        assert result.new_cursor == 10  # After "foo/"
        # Continue: 10 -> 13 (after "bar")
        state = PromptState("load /foo/bar", 10)
        result = mode.handle_key("alt+f", None, state)
        assert result.new_cursor == 13  # After "bar"

    def test_alt_f_leading_slash_is_own_unit(self) -> None:
        """Alt+F from position 0 with leading slash moves to position 1."""
        mode = EmacsEditingMode()
        state = PromptState("/foo/bar", 0)
        result = mode.handle_key("alt+f", None, state)
        assert result is not None
        assert result.new_cursor == 1  # After leading slash

    def test_alt_f_trailing_whitespace_not_absorbed(self) -> None:
        """Alt+F does not absorb trailing whitespace unless lone slash follows."""
        mode = EmacsEditingMode()
        # "foo   bar" from 0 should stop at 3 (end of foo, not absorbing spaces)
        state = PromptState("foo   bar", 0)
        result = mode.handle_key("alt+f", None, state)
        assert result is not None
        assert result.new_cursor == 3  # After "foo", not absorbing spaces
