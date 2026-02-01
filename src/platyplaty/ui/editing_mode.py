#!/usr/bin/env python3
"""Protocol-based Strategy pattern for editing modes.

This module defines the EditingMode Protocol and related types that enable
swappable editing mode implementations (e.g., emacs, vi). The Protocol-based
approach allows different editing modes to be used interchangeably without
modifying the command prompt code.

The editing mode is stored in AppContext for session-level state persistence,
allowing the yank buffer and other state to persist across prompt invocations.
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass
class PromptState:
    """Current state of the command prompt input.

    Passed to the editing mode's handle_key method to provide context
    for key handling operations.
    """

    text: str
    cursor: int


@dataclass
class EditResult:
    """Result of a key handling operation.

    Returned by the editing mode's handle_key method to indicate what
    changes should be applied to the prompt.
    """

    new_text: str
    new_cursor: int
    state_changed: bool


class EditingMode(Protocol):
    """Protocol for editing mode implementations.

    Editing modes handle keyboard input for text editing in the command
    prompt. Different implementations (e.g., emacs, vi) can provide
    different keybinding behaviors.
    """

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
        ...

    def reset_transient_state(self) -> None:
        """Reset per-prompt transient state.

        Called when the command prompt opens. Resets state like the
        consecutive cut chain tracker, but NOT the yank buffer which
        persists across prompt invocations.
        """
        ...

    def reset_cut_chain(self) -> None:
        """Break the consecutive cut chain.

        Called by handle_command_key after processing any non-emacs key
        to ensure that non-emacs actions break the consecutive cut chain.
        """
        ...


def create_editing_mode() -> EditingMode:
    """Create and return an editing mode instance.

    Factory function that creates the default editing mode. Currently
    returns an EmacsEditingMode instance. This function is used by
    AppContext for session-level state initialization.

    The import is done inside the function body (lazy import) to avoid
    circular imports, since emacs_editing.py imports from this module.

    Returns:
        An EditingMode implementation instance.
    """
    from platyplaty.ui.emacs_editing import EmacsEditingMode

    return EmacsEditingMode()
