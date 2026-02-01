#!/usr/bin/env python3
"""Emacs-style keybindings for the command prompt.

This module implements emacs-style editing keybindings similar to what users
get from `set -o emacs` in the shell. The EmacsEditingMode class implements
the EditingMode Protocol and dispatches to specialized handler modules.

The class is stored in AppContext for session-level state persistence. The
yank buffer persists across prompt invocations, while transient state (like
the consecutive cut chain tracker) resets when the prompt opens.
"""

from platyplaty.ui.editing_mode import EditResult, PromptState
from platyplaty.ui.emacs_cursor import CURSOR_HANDLERS
from platyplaty.ui.emacs_cut import (
    CutResult,
    compute_alt_d,
    compute_ctrl_k,
    compute_ctrl_u,
    compute_ctrl_w,
)
from platyplaty.ui.emacs_delete import handle_ctrl_d


class EmacsEditingMode:
    """Emacs-style editing mode implementation.

    Provides emacs keybindings for cursor movement, text editing, and
    cut/yank operations. State persists across prompt invocations.
    """

    def __init__(self) -> None:
        """Initialize with empty yank buffer and no active cut chain."""
        self._yank_buffer: str = ""
        self._last_was_cut: bool = False

    def reset_transient_state(self) -> None:
        """Reset per-prompt transient state."""
        self._last_was_cut = False

    def reset_cut_chain(self) -> None:
        """Break the consecutive cut chain."""
        self._last_was_cut = False

    def _handle_cut(self, cut_result: CutResult) -> EditResult:
        """Handle a cut operation, storing text in yank buffer.

        No-op cuts (empty cut_text) preserve cut chain state.
        """
        if not cut_result.cut_text:
            return EditResult(cut_result.new_text, cut_result.new_cursor, False)
        if self._last_was_cut:
            self._yank_buffer += cut_result.cut_text
        else:
            self._yank_buffer = cut_result.cut_text
        self._last_was_cut = True
        return EditResult(cut_result.new_text, cut_result.new_cursor, True)

    def handle_key(
        self, key: str, character: str | None, state: PromptState
    ) -> EditResult | None:
        """Handle a key press and return the result."""
        # Check cursor movement handlers
        if key in CURSOR_HANDLERS:
            self._last_was_cut = False
            return CURSOR_HANDLERS[key](state)

        # Ctrl+D: delete character at cursor
        if key == "ctrl+d":
            self._last_was_cut = False
            return handle_ctrl_d(state)

        # Ctrl+K: cut from cursor to end of line
        if key == "ctrl+k":
            return self._handle_cut(compute_ctrl_k(state))

        # Ctrl+U: cut from beginning of line to cursor
        if key == "ctrl+u":
            return self._handle_cut(compute_ctrl_u(state))

        # Ctrl+W: cut previous word (unix word definition)
        if key == "ctrl+w":
            return self._handle_cut(compute_ctrl_w(state))

        # Alt+D: cut word forward (alphanumeric word definition)
        if key in ("alt+d", "escape+d"):
            return self._handle_cut(compute_alt_d(state))

        return None

    @property
    def yank_buffer(self) -> str:
        """Return the current yank buffer contents for testing."""
        return self._yank_buffer
