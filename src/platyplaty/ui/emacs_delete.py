#!/usr/bin/env python3
"""Emacs-style delete handlers.

Pure functions for delete operations. Each function takes a PromptState
and returns an EditResult with the modified text.
"""

from platyplaty.ui.editing_mode import EditResult, PromptState


def handle_ctrl_d(state: PromptState) -> EditResult:
    """Delete character at cursor position.

    If cursor is at end of text, returns no-op (state_changed=False).
    Otherwise deletes the character at cursor and returns state_changed=True.
    """
    if state.cursor >= len(state.text):
        return EditResult(state.text, state.cursor, False)
    new_text = state.text[:state.cursor] + state.text[state.cursor + 1:]
    return EditResult(new_text, state.cursor, True)
