#!/usr/bin/env python3
"""Emacs-style cursor movement handlers.

Pure functions for cursor movement operations. Each function takes a
PromptState and returns an EditResult with the new cursor position.
"""

from platyplaty.ui.editing_mode import EditResult, PromptState
from platyplaty.ui.word_boundary import (
    find_word_end_forward,
    find_word_start_backward,
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
    """Move cursor back one word."""
    new_cursor = find_word_start_backward(state.text, state.cursor)
    moved = new_cursor != state.cursor
    return EditResult(state.text, new_cursor, moved)


def handle_alt_f(state: PromptState) -> EditResult:
    """Move cursor forward one word."""
    new_cursor = find_word_end_forward(state.text, state.cursor)
    moved = new_cursor != state.cursor
    return EditResult(state.text, new_cursor, moved)
