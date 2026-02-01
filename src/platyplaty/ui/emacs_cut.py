#!/usr/bin/env python3
"""Emacs-style cut operation helpers.

Pure functions that compute cut boundaries and text. The actual buffer
management is handled by EmacsEditingMode, which calls these helpers.
"""

from dataclasses import dataclass

from platyplaty.ui.editing_mode import PromptState


@dataclass
class CutResult:
    """Result of a cut operation computation.

    Attributes:
        cut_text: The text that would be cut (empty if no-op).
        new_text: The remaining text after the cut.
        new_cursor: The new cursor position.
    """

    cut_text: str
    new_text: str
    new_cursor: int


def compute_ctrl_k(state: PromptState) -> CutResult:
    """Compute result of Ctrl+K (cut to end of line).

    Returns CutResult with cut_text empty if cursor is at end.
    """
    cut_text = state.text[state.cursor:]
    new_text = state.text[:state.cursor]
    return CutResult(cut_text, new_text, state.cursor)


def compute_ctrl_u(state: PromptState) -> CutResult:
    """Compute result of Ctrl+U (cut to beginning of line).

    Returns CutResult with cut_text empty if cursor is at start.
    """
    cut_text = state.text[:state.cursor]
    new_text = state.text[state.cursor:]
    return CutResult(cut_text, new_text, 0)
