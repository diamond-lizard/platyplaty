"""Persistent message widget for displaying messages until dismissed.

This module provides a widget that displays messages at the bottom of
the screen that persist until the user presses any key, with black
text on a red background.
"""

from rich.segment import Segment
from rich.style import Style
from textual.reactive import reactive
from textual.strip import Strip
from textual.widget import Widget

from platyplaty.ui.transient_error import ERROR_STYLE


class PersistentMessage(Widget):
    """A persistent message bar that displays messages until dismissed.

    The bar is hidden by default. When show_message() is called, it
    displays the message in black text on red background until
    clear_message() is called.

    Attributes:
        message: The current message to display, empty when hidden.
    """

    message: reactive[str] = reactive("", repaint=True)

    DEFAULT_CSS = """
    PersistentMessage {
        height: 1;
        display: none;
    }
    PersistentMessage.visible {
        display: block;
    }
    """

    def show_message(self, text: str) -> None:
        """Display a persistent message.

        Args:
            text: The message to display.
        """
        self.message = text
        self.add_class("visible")

    def clear_message(self) -> None:
        """Clear the message and hide the widget."""
        self.message = ""
        self.remove_class("visible")

    def render_line(self, y: int) -> Strip:
        """Render a single line of the widget.

        Args:
            y: The line index to render (always 0 for this widget).

        Returns:
            A Strip containing the rendered message.
        """
        if y != 0 or not self.message:
            return Strip([])
        width = self.size.width
        text = self.message[:width].ljust(width)
        return Strip([Segment(text, ERROR_STYLE)])
