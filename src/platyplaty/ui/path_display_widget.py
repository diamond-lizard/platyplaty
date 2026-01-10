#!/usr/bin/env python3
"""Path display widget for file browser.

This module provides the PathDisplay widget that shows the current
path at the top of the file browser section.
"""

from pathlib import Path

from rich.segment import Segment
from rich.style import Style
from textual.reactive import reactive
from textual.strip import Strip
from textual.widget import Widget

from platyplaty.ui.path_orchestrator import render_path


class PathDisplay(Widget):
    """Widget displaying the current path at the top of the file browser.

    Shows the path to the currently selected item, with colors for
    different component types. Automatically abbreviates or truncates
    the path when it exceeds the available width.

    Attributes:
        path: The current path to display.
        mark_selected: Whether to mark the final component as selected.
    """

    path: reactive[Path | None] = reactive(None, repaint=True)
    mark_selected: reactive[bool] = reactive(True, repaint=True)

    DEFAULT_CSS = """
    PathDisplay {
        height: 1;
    }
    """

    def get_content_height(self, container: object, width: int) -> int:
        """Return the content height (always 1 line).

        Args:
            container: The container widget (unused).
            width: Available width (unused).

        Returns:
            Always returns 1.
        """
        return 1

    def render_line(self, y: int) -> Strip:
        """Render a single line of the widget.

        Args:
            y: The line index to render (always 0 for this widget).

        Returns:
            A Strip containing the rendered path.
        """
        if y != 0 or self.path is None:
            return Strip([])
        width = self.size.width
        if width <= 0:
            return Strip([])
        styled_text = render_path(self.path, width, self.mark_selected)
        segments = self._text_to_segments(styled_text)
        return Strip(segments)

    def _text_to_segments(self, text: object) -> list[Segment]:
        """Convert Rich Text to a list of Segments for Strip.

        Args:
            text: Rich Text object to convert.

        Returns:
            List of Segment objects.
        """
        segments: list[Segment] = []
        for span_text, style, _ in text.render(self.app.console):
            seg_style = Style.parse(str(style)) if style else None
            segments.append(Segment(span_text, seg_style))
        return segments
