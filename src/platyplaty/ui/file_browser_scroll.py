"""Scroll adjustment functions for the file browser widget.

This module provides functions for adjusting scroll position in
the left and right panes. These are package-private functions
used by the FileBrowser class.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from platyplaty.ui.file_browser_types import RightPaneDirectory
from platyplaty.ui.nav_scroll import calc_safe_zone_scroll

if TYPE_CHECKING:
    from platyplaty.ui.directory_types import DirectoryEntry
    from platyplaty.ui.file_browser import FileBrowser


def find_entry_index_in_listing(entries: list[DirectoryEntry], name: str) -> int:
    """Find the index of an entry by name in a list of entries.

    Args:
        entries: The list of directory entries to search.
        name: The name to find.

    Returns:
        Index of the entry, or 0 if not found.
    """
    gen = (i for i, e in enumerate(entries) if e.name == name)
    return next(gen, 0)


def adjust_left_pane_scroll(browser: FileBrowser, pane_height: int) -> None:
    """Adjust left pane scroll so the current directory is visible.

    Computes the index of current_dir in _left_listing and applies
    the safe-zone scroll algorithm to _left_scroll_offset. Safe to
    call multiple times (idempotent).

    Args:
        browser: The file browser instance.
        pane_height: The height of the pane in lines.
    """
    if pane_height <= 0:
        return
    if browser._left_listing is None or not browser._left_listing.entries:
        return
    current_name = browser.current_dir.name
    index = find_entry_index_in_listing(browser._left_listing.entries, current_name)
    item_count = len(browser._left_listing.entries)
    browser._left_scroll_offset = calc_safe_zone_scroll(
        index, browser._left_scroll_offset, pane_height, item_count
    )


def adjust_right_pane_scroll(browser: FileBrowser, pane_height: int) -> None:
    """Adjust right pane scroll so the selection is visible.

    Uses the remembered selection index when showing directory contents.
    Skips adjustment for file preview/error/empty states.

    Args:
        browser: The file browser instance.
        pane_height: The height of the pane in lines.
    """
    if pane_height <= 0:
        return
    if browser._right_selected_index is None:
        return
    content = browser._right_content
    if content is None or not isinstance(content, RightPaneDirectory):
        return
    listing = content.listing
    if listing is None or not listing.entries:
        return
    item_count = len(listing.entries)
    browser._right_scroll_offset = calc_safe_zone_scroll(
        browser._right_selected_index, browser._right_scroll_offset,
        pane_height, item_count,
    )
