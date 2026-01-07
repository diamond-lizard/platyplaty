"""Pane rendering functions for the file browser widget.

This module provides functions for rendering individual pane lines
in the file browser. These are package-private functions.
"""

from platyplaty.ui.directory_types import DirectoryListing
from platyplaty.ui.file_browser_types import (
    RightPaneContent,
    RightPaneDirectory,
    render_file_preview_line,
)


def render_pane_line(
    listing: DirectoryListing | None,
    y: int,
    width: int,
    is_left_pane: bool,
    scroll_offset: int = 0,
) -> str:
    """Render a single line of a pane.

    Args:
        listing: The directory listing to render.
        y: The line number to render (0-indexed).
        width: The width of the pane.
        is_left_pane: True if rendering the left pane (for root case).
        scroll_offset: Offset into the listing for scrolling (default 0).

    Returns:
        A string padded to the pane width.
    """
    if listing is None:
        return " " * width

    # Handle empty listing
    if not listing.entries:
        return _render_empty_listing(listing, y, width, is_left_pane)

    # Render entry
    if y + scroll_offset < len(listing.entries):
        name = listing.entries[y + scroll_offset].name
        return name.ljust(width)[:width]

    return " " * width


def _render_empty_listing(
    listing: DirectoryListing, y: int, width: int, is_left_pane: bool
) -> str:
    """Render a line for an empty listing."""
    if is_left_pane and listing.was_empty:
        # At filesystem root - left pane is truly empty
        return " " * width
    if y == 0:
        if listing.permission_denied:
            msg = "inaccessible directory"
        elif listing.was_empty:
            msg = "empty"
        else:
            msg = "no .milk files"
        return msg.ljust(width)[:width]
    return " " * width


def render_right_pane_line(content: RightPaneContent, y: int, width: int) -> str:
    """Render a single line of the right pane.

    Handles both directory listings and file previews.

    Args:
        content: The right pane content to render.
        y: The line number to render (0-indexed).
        width: The width of the pane.

    Returns:
        A string padded to the pane width.
    """
    if content is None:
        return " " * width
    if isinstance(content, RightPaneDirectory):
        return render_pane_line(content.listing, y, width, is_left_pane=False)
    return render_file_preview_line(content.lines, y, width)
