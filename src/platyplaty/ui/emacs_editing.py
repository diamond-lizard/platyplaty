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
from platyplaty.ui.emacs_cursor import (
    handle_alt_b,
    handle_alt_f,
    handle_ctrl_a,
    handle_ctrl_b,
    handle_ctrl_e,
    handle_ctrl_f,
)
from platyplaty.ui.emacs_delete import handle_ctrl_d

# Mapping of keys to cursor movement handlers
_CURSOR_HANDLERS = {
    "ctrl+a": handle_ctrl_a,
    "ctrl+e": handle_ctrl_e,
    "ctrl+b": handle_ctrl_b,
    "ctrl+f": handle_ctrl_f,
    "alt+b": handle_alt_b,
    "escape+b": handle_alt_b,
    "alt+f": handle_alt_f,
    "escape+f": handle_alt_f,
}


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

    def handle_key(
        self, key: str, character: str | None, state: PromptState
    ) -> EditResult | None:
        """Handle a key press and return the result."""
        # Check cursor movement handlers
        if key in _CURSOR_HANDLERS:
            self._last_was_cut = False
            return _CURSOR_HANDLERS[key](state)

        # Ctrl+D: delete character at cursor
        if key == "ctrl+d":
            self._last_was_cut = False
            return handle_ctrl_d(state)

        return None

    @property
    def yank_buffer(self) -> str:
        """Return the current yank buffer contents for testing."""
        return self._yank_buffer
