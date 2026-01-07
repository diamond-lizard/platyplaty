"""Main rendering function for the file browser widget.

This module provides the render_line function that composes all three
panes into a single line. It is a package-private function used by
the FileBrowser class.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.segment import Segment
from textual.strip import Strip

from platyplaty.ui.file_browser_pane_render import (
    render_pane_line,
    render_right_pane_line,
)
from platyplaty.ui.layout import calculate_pane_widths

if TYPE_CHECKING:
    from platyplaty.ui.file_browser import FileBrowser


def render_line(browser: FileBrowser, y: int) -> Strip:
    """Render a single line of the file browser.

    Args:
        browser: The file browser instance.
        y: The line number to render (0-indexed).

    Returns:
        A Strip containing the rendered line.
    """
    width = browser.size.width
    pane_widths = calculate_pane_widths(width)

    segments: list[Segment] = []

    # Render left pane
    if pane_widths.left > 0:
        left_text = render_pane_line(
            browser._left_listing, y, pane_widths.left, is_left_pane=True
        )
        segments.append(Segment(left_text))
        segments.append(Segment(" "))  # Gap

    # Render middle pane
    middle_text = render_pane_line(
        browser._middle_listing, y, pane_widths.middle,
        is_left_pane=False, scroll_offset=browser._middle_scroll_offset
    )
    segments.append(Segment(middle_text))
    segments.append(Segment(" "))  # Gap

    # Render right pane
    right_text = render_right_pane_line(browser._right_content, y, pane_widths.right)
    segments.append(Segment(right_text))

    return Strip(segments)
