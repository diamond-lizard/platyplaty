#!/usr/bin/env python3
"""Command prompt widget for : commands.

This module provides a widget that displays a command prompt at the
bottom of the terminal for entering commands like load, save, clear, shuffle.
"""

from collections.abc import Awaitable, Callable

from textual.events import Key, Paste
from textual.reactive import reactive
from textual.strip import Strip
from textual.widget import Widget

from platyplaty.ui.command_key import handle_command_key, return_focus_to_widget
from platyplaty.ui.command_prompt_cursor import CursorManager
from platyplaty.ui.command_render import render_command_line
from platyplaty.ui.command_prompt_paste import do_paste, do_paste_from_selection


class CommandPrompt(Widget, can_focus=True):
    """A command prompt that accepts text input for commands."""

    input_text: reactive[str] = reactive("", repaint=True)
    cursor_index: reactive[int] = reactive(0, repaint=True)
    cursor_visible: reactive[bool] = reactive(True, repaint=True)
    callback: Callable[[str], Awaitable[None]] | None = None
    previous_focus_id: str | None = None
    _cursor: "CursorManager"

    DEFAULT_CSS = """
    CommandPrompt {
        height: 1;
        display: none;
    }
    CommandPrompt.visible {
        display: block;
    }
    """

    def __init__(self) -> None:
        """Initialize the command prompt with cursor manager."""
        super().__init__()
        self._cursor = CursorManager(self)

    def show_prompt(
        self,
        callback: Callable[[str], Awaitable[None]],
        previous_focus_id: str | None = None,
        initial_text: str = "",
    ) -> None:
        """Display the command prompt and take focus."""
        self.input_text = initial_text
        self._cursor.scroll = 0
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
        self._cursor.scroll = 0
        self.cursor_index = 0
        self.callback = None
        self.remove_class("visible")
        return_focus_to_widget(self.app, self.previous_focus_id)
        self.previous_focus_id = None

    def start_blink_timer(self) -> None:
        """Start the cursor blink timer."""
        self._cursor.start_blink()

    def stop_blink_timer(self, visible: bool = True) -> None:
        """Stop the cursor blink timer and set visibility state."""
        self._cursor.stop_blink(visible)

    def on_focus(self) -> None:
        """Start blink timer when focused."""
        self.start_blink_timer()

    def on_blur(self) -> None:
        """Stop blink timer on blur."""
        self.stop_blink_timer(visible=False)

    def on_resize(self, event: object) -> None:
        """Recalculate scroll offset when widget is resized."""
        self._cursor.handle_resize(self.cursor_index, self.size.width - 1)

    def update_cursor_with_scroll(self, new_cursor: int) -> None:
        """Update cursor position and scroll offset to keep cursor visible."""
        self._cursor.update_position(new_cursor, self.size.width - 1)

    def paste_text(self, text: str) -> bool:
        """Paste text at cursor, stripping whitespace."""
        return do_paste(self, text)

    def paste_from_selection(self) -> bool:
        """Paste X11 primary selection at cursor."""
        return do_paste_from_selection(self)

    def on_paste(self, event: Paste) -> None:
        """Handle bracketed paste events from terminal."""
        event.stop()
        do_paste(self, event.text)

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
            self._cursor.scroll,
            self.cursor_index,
            self.cursor_visible,
        )
