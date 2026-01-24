#!/usr/bin/env python3
"""Command prompt widget for : commands.

This module provides a widget that displays a command prompt at the
bottom of the terminal for entering commands like load, save, clear, shuffle.
"""

from collections.abc import Awaitable, Callable

from rich.segment import Segment
from rich.style import Style
from textual.events import Key
from textual.reactive import reactive
from textual.strip import Strip
from textual.widget import Widget

from platyplaty.ui.command_key import handle_command_key, return_focus_to_widget

PROMPT_STYLE = Style(color="white", bgcolor="black")


class CommandPrompt(Widget, can_focus=True):
    """A command prompt that accepts text input for commands."""

    input_text: reactive[str] = reactive("", repaint=True)
    cursor_index: reactive[int] = reactive(0, repaint=True)
    callback: Callable[[str], Awaitable[None]] | None = None
    previous_focus_id: str | None = None

    DEFAULT_CSS = """
    CommandPrompt {
        dock: bottom;
        height: 1;
        display: none;
    }
    CommandPrompt.visible {
        display: block;
    }
    """

    def show_prompt(
        self,
        callback: Callable[[str], Awaitable[None]],
        previous_focus_id: str | None = None,
        initial_text: str = "",
    ) -> None:
        """Display the command prompt and take focus."""
        self.input_text = initial_text
        self.cursor_index = len(initial_text)
        self.callback = callback
        self.previous_focus_id = previous_focus_id
        self.add_class("visible")
        self.focus()

    def hide(self) -> None:
        """Hide the prompt and return focus."""
        self.input_text = ""
        self.cursor_index = 0
        self.callback = None
        self.remove_class("visible")
        self._return_focus()

    def _return_focus(self) -> None:
        """Return focus to the previously focused widget."""
        return_focus_to_widget(self.app, self.previous_focus_id)
        self.previous_focus_id = None

    async def on_key(self, event: Key) -> None:
        """Handle key events for the command prompt."""
        event.stop()
        await handle_command_key(event.key, self, event.character)

    def render_line(self, y: int) -> Strip:
        """Render a single line of the widget."""
        if y != 0:
            return Strip([])
        width = self.size.width
        text = (":" + self.input_text)[:width].ljust(width)
        return Strip([Segment(text, PROMPT_STYLE)])
