"""Error view rendering module.

Renders header, content, and footer lines for the error view.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.segment import Segment
from rich.style import Style
from textual.strip import Strip

if TYPE_CHECKING:
    from platyplaty.ui.error_view import ErrorView

# Styles for error view content
_HEADER_STYLE = Style(color="white", bgcolor="black")
_CONTENT_STYLE = Style(color="white", bgcolor="black")
_EMPTY_STYLE = Style(color="grey50", bgcolor="black")
_FOOTER_STYLE = Style(color="black", bgcolor="white")

_HEADER_TEXT = "Renderer Errors"
_EMPTY_TEXT = "No errors"
_FOOTER_TEXT = "Escape: return | c: clear"


def render_line(view: ErrorView, y: int, width: int) -> Strip:
    """Render a single line of the error view.

    Args:
        view: The ErrorView widget.
        y: The line number (0-indexed).
        width: The terminal width.

    Returns:
        A Strip for the line.
    """
    if y == 0:
        return _render_header(width)
    if y == view.size.height - 1:
        return _render_footer(width)
    return _render_content_line(view, y - 1, width)


def _render_header(width: int) -> Strip:
    """Render the header line."""
    text = _HEADER_TEXT.ljust(width)
    return Strip([Segment(text, _HEADER_STYLE)])


def _render_footer(width: int) -> Strip:
    """Render the footer line with hints."""
    text = _FOOTER_TEXT.ljust(width)
    return Strip([Segment(text, _FOOTER_STYLE)])


def _render_content_line(view: ErrorView, content_y: int, width: int) -> Strip:
    """Render a content line (error message or empty state).

    Args:
        view: The ErrorView widget.
        content_y: The content line index (0-indexed, excludes header).
        width: The terminal width.

    Returns:
        A Strip for the content line.
    """
    if not view._wrapped_lines:
        return _render_empty_state(content_y, width)
    line_index = view._scroll_offset + content_y
    if line_index >= len(view._wrapped_lines):
        return Strip([Segment(" " * width, _CONTENT_STYLE)])
    text = view._wrapped_lines[line_index].ljust(width)
    return Strip([Segment(text, _CONTENT_STYLE)])


def _render_empty_state(content_y: int, width: int) -> Strip:
    """Render the empty state message on the first content line."""
    if content_y == 0:
        text = _EMPTY_TEXT.ljust(width)
        return Strip([Segment(text, _EMPTY_STYLE)])
    return Strip([Segment(" " * width, _CONTENT_STYLE)])
