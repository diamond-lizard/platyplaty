"""Right pane rendering functions for the file browser widget.

This module provides functions for rendering individual lines
in the right pane. These are package-private functions.
"""

from rich.segment import Segment
from rich.style import Style

from platyplaty.ui.colors import BACKGROUND_COLOR, FILE_COLOR
from platyplaty.ui.file_browser_pane_render import render_pane_line
from platyplaty.ui.file_browser_types import (
    RightPaneContent,
    RightPaneDirectory,
    render_file_preview_line,
)


def render_right_pane_line(
    content: RightPaneContent, y: int, width: int
) -> list[Segment]:
    """Render a single line of the right pane.

    Handles both directory listings and file previews.

    Args:
        content: The right pane content to render.
        y: The line number to render (0-indexed).
        width: The width of the pane.

    Returns:
        A list of Segments with appropriate styling.
    """
    bg_style = Style(bgcolor=BACKGROUND_COLOR)
    if content is None:
        return [Segment(" " * width, bg_style)]
    if isinstance(content, RightPaneDirectory):
        return render_pane_line(content.listing, y, width, is_left_pane=False)
    # File preview - white text
    text = render_file_preview_line(content.lines, y, width)
    style = Style(color=FILE_COLOR, bgcolor=BACKGROUND_COLOR)
    return [Segment(text, style)]
