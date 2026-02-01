#!/usr/bin/env python3
"""Emacs-style keybindings for the command prompt.

This module implements emacs-style editing keybindings similar to what users
get from `set -o emacs` in the shell. It provides cursor movement, text
deletion, cut/yank operations, and word navigation.

The EmacsEditingMode class implements the EditingMode Protocol and is stored
in AppContext for session-level state persistence. The yank buffer persists
across prompt invocations, while transient state (like the consecutive cut
chain tracker) resets when the prompt opens.
"""

from platyplaty.ui.editing_mode import EditResult, PromptState


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
        """Reset per-prompt transient state.

        Called when the command prompt opens. Resets the consecutive cut
        chain tracker but NOT the yank buffer, which persists across
        prompt invocations.
        """
        self._last_was_cut = False

    def reset_cut_chain(self) -> None:
        """Break the consecutive cut chain.

        Called by handle_command_key after processing any non-emacs key
        to ensure that non-emacs actions break the consecutive cut chain.
        """
        self._last_was_cut = False

    def handle_key(
        self, key: str, character: str | None, state: PromptState
    ) -> EditResult | None:
        """Handle a key press and return the result.

        Args:
            key: The key name (e.g., "ctrl+a", "alt+b").
            character: The character representation, if printable.
            state: Current prompt state (text and cursor position).

        Returns:
            EditResult if the key was handled, None if not handled.
        """
        # Ctrl+A: move cursor to beginning of line
        if key == "ctrl+a":
            self._last_was_cut = False
            moved = state.cursor != 0
            return EditResult(state.text, 0, moved)

        # Ctrl+E: move cursor to end of line
        if key == "ctrl+e":
            self._last_was_cut = False
            end = len(state.text)
            moved = state.cursor != end
            return EditResult(state.text, end, moved)

        # Ctrl+B: move cursor back one character
        if key == "ctrl+b":
            self._last_was_cut = False
            new_cursor = max(0, state.cursor - 1)
            moved = new_cursor != state.cursor
            return EditResult(state.text, new_cursor, moved)

        # Ctrl+F: move cursor forward one character
        if key == "ctrl+f":
            self._last_was_cut = False
            end = len(state.text)
            new_cursor = min(end, state.cursor + 1)
            moved = new_cursor != state.cursor
            return EditResult(state.text, new_cursor, moved)

        return None

    @property
    def yank_buffer(self) -> str:
        """Return the current yank buffer contents for testing."""
        return self._yank_buffer
