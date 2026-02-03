#!/usr/bin/env python3
"""Emacs-style cursor movement handlers.

Pure functions for cursor movement operations. Each function takes a
PromptState and returns an EditResult with the new cursor position.
"""

from platyplaty.ui.editing_mode import EditResult, PromptState
from platyplaty.ui.path_boundary import (
    find_path_component_start_backward,
    find_path_word_end_forward,
)


def handle_ctrl_a(state: PromptState) -> EditResult:
    """Move cursor to beginning of line."""
    moved = state.cursor != 0
    return EditResult(state.text, 0, moved)


def handle_ctrl_e(state: PromptState) -> EditResult:
    """Move cursor to end of line."""
    end = len(state.text)
    moved = state.cursor != end
    return EditResult(state.text, end, moved)


def handle_ctrl_b(state: PromptState) -> EditResult:
    """Move cursor back one character."""
    new_cursor = max(0, state.cursor - 1)
    moved = new_cursor != state.cursor
    return EditResult(state.text, new_cursor, moved)


def handle_ctrl_f(state: PromptState) -> EditResult:
    """Move cursor forward one character."""
    end = len(state.text)
    new_cursor = min(end, state.cursor + 1)
    moved = new_cursor != state.cursor
    return EditResult(state.text, new_cursor, moved)


def handle_alt_b(state: PromptState) -> EditResult:
    """Move cursor back one path component."""
    new_cursor = find_path_component_start_backward(state.text, state.cursor)
    moved = new_cursor != state.cursor
    return EditResult(state.text, new_cursor, moved)


def handle_alt_f(state: PromptState) -> EditResult:
    """Move cursor forward one path component."""
    new_cursor = find_path_word_end_forward(state.text, state.cursor)
    moved = new_cursor != state.cursor
    return EditResult(state.text, new_cursor, moved)


# Mapping of keys to cursor movement handlers
CURSOR_HANDLERS = {
    "ctrl+a": handle_ctrl_a,
    "ctrl+e": handle_ctrl_e,
    "ctrl+b": handle_ctrl_b,
    "ctrl+f": handle_ctrl_f,
    "alt+b": handle_alt_b,
    "escape+b": handle_alt_b,
    "alt+f": handle_alt_f,
    "escape+f": handle_alt_f,
    # Workaround for Textual issue #6192: In xterm and other terminals,
    # pressing Alt+F sends ESC followed by 'f' (the standard escape sequence
    # for Alt+letter). However, Textual's key parser incorrectly interprets
    # this sequence as ctrl+right instead of alt+f. Similarly, Alt+B is
    # misinterpreted as ctrl+left. This appears to be a timing issue where
    # ESC and the letter arrive as separate events, and Textual's parser
    # matches them against the wrong key definition. By mapping ctrl+right
    # and ctrl+left to the word movement handlers, we ensure Alt+F and Alt+B
    # work correctly even when Textual misreports them.
    #
    # More information in https://github.com/Textualize/textual/issues/6192
    "ctrl+right": handle_alt_f,
    "ctrl+left": handle_alt_b,
}
