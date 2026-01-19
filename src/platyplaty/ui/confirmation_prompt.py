#!/usr/bin/env python3
"""Confirmation prompt widget for y/n prompts.

This module provides a widget that displays confirmation prompts at the
bottom of the terminal, accepting only 'y' or 'n' keys.
"""

from collections.abc import Awaitable, Callable

from rich.segment import Segment
from rich.style import Style
from textual.events import Key
from textual.reactive import reactive
from textual.strip import Strip
from textual.widget import Widget

from platyplaty.ui.confirmation_key import handle_confirmation_key, return_focus_to_widget

PROMPT_STYLE = Style(color="black", bgcolor="red")


class ConfirmationPrompt(Widget, can_focus=True):
    """A confirmation prompt that accepts only y or n."""

    message: reactive[str] = reactive("", repaint=True)
    callback: Callable[[bool], Awaitable[None]] | None = None
    previous_focus_id: str | None = None

    DEFAULT_CSS = """
    ConfirmationPrompt {
        dock: bottom;
        height: 1;
        display: none;
    }
    ConfirmationPrompt.visible {
        display: block;
    }
    """

    def show_prompt(
        self,
        text: str,
        callback: Callable[[bool], Awaitable[None]],
        previous_focus_id: str | None = None,
    ) -> None:
        """Display a confirmation prompt and take focus."""
        self.message = text
        self.callback = callback
        self.previous_focus_id = previous_focus_id
        self.add_class("visible")
        self.focus()

    def _hide(self) -> None:
        """Hide the prompt and return focus."""
        self.message = ""
        self.callback = None
        self.remove_class("visible")
        self._return_focus()

    def _return_focus(self) -> None:
        """Return focus to the previously focused widget."""
        return_focus_to_widget(self.app, self.previous_focus_id)
        self.previous_focus_id = None

    async def on_key(self, event: Key) -> None:
        """Handle key events, only accepting y or n."""
        event.stop()
        await handle_confirmation_key(event.key, self.callback, self._hide)

    def render_line(self, y: int) -> Strip:
        """Render a single line of the widget."""
        if y != 0 or not self.message:
            return Strip([])
        width = self.size.width
        text = self.message[:width].ljust(width)
        return Strip([Segment(text, PROMPT_STYLE)])
