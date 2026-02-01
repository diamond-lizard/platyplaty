#!/usr/bin/env python3
"""Yank (paste) operation for emacs-style editing.

This module implements Ctrl+Y to paste from the internal yank buffer.
"""

from platyplaty.ui.editing_mode import EditResult, PromptState


def compute_yank(state: PromptState, yank_buffer: str) -> EditResult:
    """Compute the result of yanking text at cursor position.

    Args:
        state: Current prompt state (text and cursor position).
        yank_buffer: Text to insert at cursor.

    Returns:
        EditResult with text after insertion, new cursor position,
        and state_changed=True if buffer was non-empty, False otherwise.
    """
    if not yank_buffer:
        return EditResult(state.text, state.cursor, False)
    pos = state.cursor
    new_text = state.text[:pos] + yank_buffer + state.text[pos:]
    new_cursor = pos + len(yank_buffer)
    return EditResult(new_text, new_cursor, True)
