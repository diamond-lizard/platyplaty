"""Render logic for the status line widget.

Handles content formatting and truncation for the status line.
"""

from typing import TYPE_CHECKING

from rich.segment import Segment
from rich.style import Style
from textual.strip import Strip

from platyplaty.ui.status_line import STATUS_LINE_STYLE
from platyplaty.ui.status_line_content import build_status_content

if TYPE_CHECKING:
    from platyplaty.ui.status_line import StatusLine

# Error indicator: red foreground on blue background (StatusLine bg)
ERROR_INDICATOR_STYLE = Style(color="red", bgcolor="blue")


def render_status_line(widget: "StatusLine", width: int) -> Strip:
    """Render the status line content with error indicator.

    Args:
        widget: The StatusLine widget with state.
        width: Available width in characters.

    Returns:
        A Strip containing the rendered status line.
    """
    has_errors = bool(widget._error_log)
    content_width = width - 1 if has_errors else width
    content = build_status_content(
        widget._autoplay_enabled,
        widget._playlist_filename,
        widget._dirty,
        content_width,
    )
    padded = content.ljust(content_width)
    segments = [Segment(padded, STATUS_LINE_STYLE)]
    if has_errors:
        segments.append(Segment("E", ERROR_INDICATOR_STYLE))
    return Strip(segments)
