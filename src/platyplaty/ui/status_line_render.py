"""Render logic for the status line widget.

Handles content formatting and truncation for the status line.
"""

from pathlib import Path
from typing import TYPE_CHECKING

from rich.segment import Segment
from textual.strip import Strip

from platyplaty.ui.status_line import STATUS_LINE_STYLE
from platyplaty.ui.status_line_content import build_status_content

if TYPE_CHECKING:
    from platyplaty.ui.status_line import StatusLine


def render_status_line(widget: "StatusLine", width: int) -> Strip:
    """Render the status line content with proper truncation.

    Args:
        widget: The StatusLine widget with state.
        width: Available width in characters.

    Returns:
        A Strip containing the rendered status line.
    """
    content = build_status_content(
        widget._autoplay_enabled,
        widget._playlist_filename,
        widget._dirty,
        width,
    )
    padded = content.ljust(width)
    return Strip([Segment(padded, STATUS_LINE_STYLE)])
