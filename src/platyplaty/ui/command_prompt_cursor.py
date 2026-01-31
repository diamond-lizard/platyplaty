#!/usr/bin/env python3
"""Cursor behavior management for command prompt.

This module provides cursor position, scrolling, and blink timer management
for the CommandPrompt widget, extracted to reduce file size.
"""

from typing import TYPE_CHECKING

from textual.timer import Timer

from platyplaty.ui.command_render import BLINK_INTERVAL_MS, calculate_scroll_offset

if TYPE_CHECKING:
    from platyplaty.ui.command_prompt import CommandPrompt


class CursorManager:
    """Manages cursor position, scrolling, and blinking for a widget."""

    def __init__(self, widget: "CommandPrompt") -> None:
        """Initialize with reference to the widget."""
        self._widget = widget
        self._timer: Timer | None = None
        self._scroll: int = 0

    @property
    def scroll(self) -> int:
        """Current horizontal scroll offset."""
        return self._scroll

    @scroll.setter
    def scroll(self, value: int) -> None:
        """Set horizontal scroll offset."""
        self._scroll = value

    def start_blink(self) -> None:
        """Start cursor blinking, making cursor visible first."""
        self.stop_blink()
        self._widget.cursor_visible = True
        self._timer = self._widget.set_interval(
            BLINK_INTERVAL_MS / 1000.0,
            self._toggle_visible,
        )

    def stop_blink(self, visible: bool = True) -> None:
        """Stop cursor blinking and set visibility state."""
        if self._timer is not None:
            self._timer.stop()
            self._timer = None
        self._widget.cursor_visible = visible

    def _toggle_visible(self) -> None:
        """Toggle cursor visibility state."""
        self._widget.cursor_visible = not self._widget.cursor_visible

    def update_position(self, new_cursor: int, visible_width: int) -> None:
        """Update cursor position and scroll offset to keep cursor visible."""
        self._scroll = calculate_scroll_offset(new_cursor, self._scroll, visible_width)
        self._widget.cursor_index = new_cursor

    def handle_resize(self, cursor_index: int, visible_width: int) -> None:
        """Recalculate scroll offset for new terminal width."""
        self._scroll = calculate_scroll_offset(
            cursor_index, self._scroll, visible_width
        )
