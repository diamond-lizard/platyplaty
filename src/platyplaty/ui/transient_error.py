"""Transient error bar widget for displaying brief error messages.

This module provides a widget that displays error messages at the
bottom of the screen for a brief duration (0.5 seconds) with black
text on a red background.
"""

from rich.segment import Segment
from rich.style import Style
from textual.app import App
from textual.reactive import reactive
from textual.strip import Strip
from textual.widget import Widget

# Duration to show the error message in seconds
ERROR_DISPLAY_DURATION = 0.5

# Styling for the error bar
ERROR_STYLE = Style(color="black", bgcolor="red")


class TransientErrorBar(Widget):
    """A transient error bar that displays messages briefly.

    The bar is hidden by default. When show() is called with a message,
    it displays the message in black text on red background for 0.5
    seconds, then automatically hides.

    Attributes:
        message: The current message to display, empty when hidden.
    """

    message: reactive[str] = reactive("", repaint=True)

    DEFAULT_CSS = """
    TransientErrorBar {
        dock: bottom;
        height: 1;
        display: none;
    }
    TransientErrorBar.visible {
        display: block;
    }
    """

    def show_error(self, text: str) -> None:
        """Display an error message for the configured duration.

        Args:
            text: The error message to display.
        """
        self.message = text
        self.add_class("visible")
        self.set_timer(ERROR_DISPLAY_DURATION, self._hide)

    def _hide(self) -> None:
        """Hide the error bar after the timer expires."""
        self.message = ""
        self.remove_class("visible")

    def render_line(self, y: int) -> Strip:
        """Render a single line of the widget.

        Args:
            y: The line index to render (always 0 for this widget).

        Returns:
            A Strip containing the rendered error message.
        """
        if y != 0 or not self.message:
            return Strip([])
        width = self.size.width
        text = self.message[:width].ljust(width)
        return Strip([Segment(text, ERROR_STYLE)])


def show_transient_error(app: "App[None]", message: str) -> None:
    """Show a transient error message at the bottom of the screen.

    Displays black text on red background for 0.5 seconds.

    Args:
        app: The Textual application instance.
        message: The error message to display.
    """
    try:
        error_bar = app.query_one("#transient_error", TransientErrorBar)
        error_bar.show_error(message)
    except Exception:
        pass
