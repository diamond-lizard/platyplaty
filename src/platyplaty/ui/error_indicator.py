"""Error indicator widget for showing "E" when errors exist.

Displays a red "E" in the bottom-right corner of the screen when
the error log contains messages. Disappears when errors are cleared.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from textual.app import App

from rich.segment import Segment
from rich.style import Style
from textual.strip import Strip
from textual.widget import Widget

ERROR_INDICATOR_STYLE = Style(color="red", bgcolor="black")


class ErrorIndicator(Widget):
    """Widget displaying "E" when errors exist in the error log.

    Positioned in the bottom-right corner. Hidden when no errors.
    """

    DEFAULT_CSS = """
    ErrorIndicator {
        dock: bottom;
        height: 1;
        display: none;
    }
    ErrorIndicator.visible {
        display: block;
    }
    """

    def __init__(
        self,
        error_log: list[str],
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize the ErrorIndicator widget."""
        super().__init__(name=name, id=id, classes=classes)
        self._error_log = error_log

    def render_line(self, y: int) -> Strip:
        """Render the error indicator."""
        if y != 0:
            return Strip([])
        width = self.size.width
        padding = " " * (width - 1)
        return Strip([Segment(padding + "E", ERROR_INDICATOR_STYLE)])

    def update_visibility(self) -> None:
        """Update visibility based on whether errors exist."""
        if self._error_log:
            self.add_class("visible")
        else:
            self.remove_class("visible")
        self.refresh()


def update_error_indicator(app: "App[None]") -> None:
    """Update the error indicator visibility.
    
    Call this after adding or clearing errors in the error log.
    
    Args:
        app: The Textual application instance.
    """
    try:
        indicator = app.query_one("#error_indicator", ErrorIndicator)
        indicator.update_visibility()
    except Exception:
        pass
