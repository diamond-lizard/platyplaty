#!/usr/bin/env python3
"""Command prompt widget for : commands.

This module provides a widget that displays a command prompt at the
bottom of the terminal for entering commands like load, save, clear, shuffle.
"""

from collections.abc import Awaitable, Callable

from rich.segment import Segment
from rich.style import Style
from textual.events import Key
from textual.timer import Timer
from textual.reactive import reactive
from textual.strip import Strip
from textual.widget import Widget

from platyplaty.ui.command_key import handle_command_key, return_focus_to_widget

PROMPT_STYLE = Style(color="white", bgcolor="black")
BLINK_INTERVAL_MS = 500


class CommandPrompt(Widget, can_focus=True):
    """A command prompt that accepts text input for commands."""

    input_text: reactive[str] = reactive("", repaint=True)
    cursor_index: reactive[int] = reactive(0, repaint=True)
    cursor_visible: reactive[bool] = reactive(True, repaint=True)
    callback: Callable[[str], Awaitable[None]] | None = None
    previous_focus_id: str | None = None
    _blink_timer: Timer | None = None

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

    def start_blink_timer(self) -> None:
        """Start the cursor blink timer, toggling visibility each interval."""
        self.stop_blink_timer(visible=True)
        self._blink_timer = self.set_interval(
            BLINK_INTERVAL_MS / 1000.0,
            self._toggle_cursor_visibility,
        )

    def _toggle_cursor_visibility(self) -> None:
        """Toggle the cursor visibility state."""
        self.cursor_visible = not self.cursor_visible

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
