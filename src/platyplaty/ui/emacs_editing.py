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
        # Handlers will be added in subsequent phases
        return None

    @property
    def yank_buffer(self) -> str:
        """Return the current yank buffer contents for testing."""
        return self._yank_buffer
