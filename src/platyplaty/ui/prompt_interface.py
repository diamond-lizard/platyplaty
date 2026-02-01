#!/usr/bin/env python3
"""PromptInterface Protocol for command key handler decoupling.

This module defines the interface that command key handlers depend on,
decoupling them from Textual's CommandPrompt widget. This follows the
"Don't Mock What You Don't Own" principle, enabling the use of a
TestPrompt Fake in tests instead of MagicMock.
"""

from collections.abc import Awaitable, Callable
from typing import Protocol


class PromptInterface(Protocol):
    """Interface for command prompt functionality used by key handlers."""

    @property
    def input_text(self) -> str:
        """Get the current input text."""
        ...

    @input_text.setter
    def input_text(self, value: str) -> None:
        """Set the input text."""
        ...

    @property
    def cursor_index(self) -> int:
        """Get the current cursor position."""
        ...

    @cursor_index.setter
    def cursor_index(self, value: int) -> None:
        """Set the cursor position."""
        ...

    @property
    def callback(self) -> Callable[[str], Awaitable[None]] | None:
        """Get the callback to invoke on command submission."""
        ...

    def update_cursor_with_scroll(self, new_cursor: int) -> None:
        """Update cursor position and scroll offset to keep cursor visible."""
        ...

    def hide(self) -> None:
        """Hide the prompt and return focus to previous widget."""
        ...

    def paste_from_selection(self) -> bool:
        """Paste from X11 primary selection, returns True if text changed."""
        ...
