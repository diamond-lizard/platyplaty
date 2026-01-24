#!/usr/bin/env python3
"""Command prompt widget for : commands.

This module provides a widget that displays a command prompt at the
bottom of the terminal for entering commands like load, save, clear, shuffle.
"""

from collections.abc import Awaitable, Callable

from textual.events import Key
from textual.reactive import reactive
from textual.strip import Strip
from textual.timer import Timer
from textual.widget import Widget

from platyplaty.ui.command_key import handle_command_key, return_focus_to_widget
from platyplaty.ui.command_render import (
    BLINK_INTERVAL_MS,
    calculate_scroll_offset,
    render_command_line,
)


class CommandPrompt(Widget, can_focus=True):
    """A command prompt that accepts text input for commands."""

    input_text: reactive[str] = reactive("", repaint=True)
    cursor_index: reactive[int] = reactive(0, repaint=True)
    cursor_visible: reactive[bool] = reactive(True, repaint=True)
    callback: Callable[[str], Awaitable[None]] | None = None
    previous_focus_id: str | None = None
    _blink_timer: Timer | None = None
    _text_scroll: int = 0

    CSS_PATH = "command_prompt.tcss"

    def show_prompt(
        self,
        callback: Callable[[str], Awaitable[None]],
        previous_focus_id: str | None = None,
        initial_text: str = "",
    ) -> None:
        """Display the command prompt and take focus."""
        self.input_text = initial_text
        self._text_scroll = 0
        self.cursor_index = len(initial_text)
        self.callback = callback
        self.previous_focus_id = previous_focus_id
        self.add_class("visible")
        self.focus()
        self.start_blink_timer()

    def hide(self) -> None:
        """Hide the prompt and return focus."""
        self.stop_blink_timer()
        self.input_text = ""
        self._text_scroll = 0
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

    def stop_blink_timer(self, visible: bool = True) -> None:
        """Stop the cursor blink timer and set visibility state."""
        if self._blink_timer is not None:
            self._blink_timer.stop()
            self._blink_timer = None
        self.cursor_visible = visible

    def _toggle_cursor_visibility(self) -> None:
        """Toggle the cursor visibility state."""
        self.cursor_visible = not self.cursor_visible

    def on_focus(self) -> None:
        """Start blink timer when focused."""
        self.start_blink_timer()

    def on_blur(self) -> None:
        """Stop blink timer on blur (defensive fallback for unexpected focus loss)."""
        self.stop_blink_timer(visible=False)

    def on_resize(self, event: object) -> None:
        """Recalculate scroll offset when widget is resized."""
        visible_width = self.size.width - 1
        self._text_scroll = calculate_scroll_offset(
            self.cursor_index, self._text_scroll, visible_width
        )

    def update_cursor_with_scroll(self, new_cursor: int) -> None:
        """Update cursor position and scroll offset to keep cursor visible."""
        visible_width = self.size.width - 1
        self._text_scroll = calculate_scroll_offset(
            new_cursor, self._text_scroll, visible_width
        )
        self.cursor_index = new_cursor

    async def on_key(self, event: Key) -> None:
        """Handle key events for the command prompt."""
        event.stop()
        state_changed = await handle_command_key(event.key, self, event.character)
        if state_changed:
            self.start_blink_timer()


    def render_line(self, y: int) -> Strip:
        """Render a single line of the widget."""
        if y != 0:
            return Strip([])
        return render_command_line(
            self.size.width,
            self.input_text,
            self._text_scroll,
            self.cursor_index,
            self.cursor_visible,
        )
