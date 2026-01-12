"""Pane rendering functions for the file browser widget.

This module provides functions for rendering individual pane lines
in the file browser. These are package-private functions.
"""

from rich.segment import Segment
from rich.style import Style

from platyplaty.ui.colors import (
    BACKGROUND_COLOR,
    EMPTY_MESSAGE_BG,
    EMPTY_MESSAGE_FG,
)
from platyplaty.ui.directory_types import DirectoryListing
from platyplaty.ui.file_browser_entry_render import (
    render_normal_entry,
    render_selected_entry,
)


def render_pane_line(
    listing: DirectoryListing | None,
    y: int,
    width: int,
    is_left_pane: bool,
    scroll_offset: int = 0,
    selected_index: int | None = None,
    show_indicators: bool = True,
) -> list[Segment]:
    """Render a single line of a pane.

    Args:
        listing: The directory listing to render.
        y: The line number to render (0-indexed).
        width: The width of the pane.
        is_left_pane: True if rendering the left pane (for root case).
        scroll_offset: Offset into the listing for scrolling (default 0).
        selected_index: Index of selected item for highlighting (None for no selection).
        show_indicators: True to display indicators (count/size) for entries.

    Returns:
        A list of Segments with appropriate styling.
    """
    bg_style = Style(bgcolor=BACKGROUND_COLOR)
    if listing is None:
        return [Segment(" " * width, bg_style)]

    # Handle empty listing
    if not listing.entries:
        return _render_empty_listing(listing, y, width, is_left_pane)

    # Render entry
    if y + scroll_offset < len(listing.entries):
        entry = listing.entries[y + scroll_offset]
        entry_idx = y + scroll_offset
        is_selected = selected_index is not None and entry_idx == selected_index
        if is_selected:
            return render_selected_entry(entry, width, show_indicators)
        return render_normal_entry(entry, width, show_indicators)

    return [Segment(" " * width, bg_style)]

def _render_empty_listing(
    listing: DirectoryListing, y: int, width: int, is_left_pane: bool
) -> list[Segment]:
    """Render a line for an empty listing."""
    bg_style = Style(bgcolor=BACKGROUND_COLOR)
    if is_left_pane and listing.was_empty:
        # At filesystem root - left pane is truly empty
        return [Segment(" " * width, bg_style)]
    if y == 0:
        if listing.permission_denied:
            msg = "inaccessible directory"
        elif listing.was_empty:
            msg = "empty"
        else:
            msg = "no .milk files"
        text = msg.ljust(width)[:width]
        style = Style(color=EMPTY_MESSAGE_FG, bgcolor=EMPTY_MESSAGE_BG)
        return [Segment(text, style)]
    return [Segment(" " * width, bg_style)]

