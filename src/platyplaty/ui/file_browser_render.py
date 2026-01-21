"""Main rendering function for the file browser widget.

This module provides the render_line function that composes all three
panes into a single line. It is a package-private function used by
the FileBrowser class.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.segment import Segment
from rich.style import Style
from textual.strip import Strip

from platyplaty.ui.colors import BACKGROUND_COLOR
from platyplaty.ui.file_browser_pane_render import render_pane_line
from platyplaty.ui.file_browser_path_render import (
    get_display_path,
    render_path,
    should_mark_selected,
    text_to_segments,
)
from platyplaty.ui.file_browser_right_pane_render import render_right_pane_line
from platyplaty.ui.layout import calculate_pane_widths

if TYPE_CHECKING:
    from platyplaty.ui.file_browser import FileBrowser


def _calc_left_selected_index(browser: FileBrowser) -> int | None:
    """Calculate selected index for left pane (current dir in parent listing)."""
    if browser._left_listing is None or not browser._left_listing.entries:
        return None
    current_name = browser.current_dir.name
    for i, entry in enumerate(browser._left_listing.entries):
        if entry.name == current_name:
            return i
    return None

def render_line(browser: FileBrowser, y: int) -> Strip:
    """Render a single line of the file browser.

    Args:
        browser: The file browser instance.
        y: The line number to render (0-indexed).

    Returns:
        A Strip containing the rendered line.
    """
    width = browser.size.width
    # y=0 is the path display line
    if y == 0:
        path = get_display_path(browser)
        mark_selected = should_mark_selected(browser)
        path_text = render_path(path, width, mark_selected)
        path_segments = text_to_segments(path_text, browser.app.console)
        return Strip(path_segments)

    layout_state = browser._layout_state
    pane_widths = calculate_pane_widths(width, layout_state)
    pane_y = y - 1  # Panes start at y=1, so subtract 1

    segments: list[Segment] = []

    # Render left pane
    if pane_widths.left > 0:
        left_segments = render_pane_line(
            browser._left_listing, pane_y, pane_widths.left, is_left_pane=True,
            scroll_offset=browser._left_scroll_offset,
            selected_index=_calc_left_selected_index(browser),
            show_indicators=False, focused=browser._focused
        )
        segments.extend(left_segments)
        segments.append(Segment(" ", Style(bgcolor=BACKGROUND_COLOR)))  # Gap

    # Render middle pane
    middle_segments = render_pane_line(
        browser._middle_listing, pane_y, pane_widths.middle,
        is_left_pane=False, scroll_offset=browser._middle_scroll_offset,
        selected_index=browser.selected_index, show_indicators=True, focused=browser._focused
    )
    segments.extend(middle_segments)
    segments.append(Segment(" ", Style(bgcolor=BACKGROUND_COLOR)))  # Gap

    # Render right pane
    right_segments = render_right_pane_line(
        browser._right_content, pane_y, pane_widths.right,
        scroll_offset=browser._right_scroll_offset,
        selected_index=browser._right_selected_index,
        focused=browser._focused,
    )
    segments.extend(right_segments)

    return Strip(segments)
