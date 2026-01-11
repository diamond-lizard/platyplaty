"""Sync and refresh functions for the file browser widget.

This module provides functions for syncing navigation state and
triggering pane refreshes. These are package-private functions
used by the FileBrowser class.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from platyplaty.ui.directory_types import DirectoryListing
from platyplaty.ui.file_browser_refresh import refresh_listings
from platyplaty.ui.file_browser_scroll import (
    adjust_left_pane_scroll,
    adjust_right_pane_scroll,
)

if TYPE_CHECKING:
    from platyplaty.ui.file_browser import FileBrowser


def find_entry_index(listing: DirectoryListing, name: str) -> int:
    """Find the index of an entry by name.

    Args:
        listing: The directory listing to search.
        name: The name to find.

    Returns:
        Index of the entry, or 0 if not found.
    """
    gen = (i for i, e in enumerate(listing.entries) if e.name == name)
    return next(gen, 0)


def sync_from_nav_state(browser: FileBrowser) -> None:
    """Sync FileBrowser state from NavigationState.

    Updates current_dir, selected_index, and scroll offset from nav state.

    Args:
        browser: The file browser instance.
    """
    browser.current_dir = browser._nav_state.current_dir
    listing = browser._nav_state.get_listing()
    if listing is None or not listing.entries:
        browser.selected_index = None
        return
    selected_entry = browser._nav_state.get_selected_entry()
    if selected_entry is None:
        browser.selected_index = None
        return
    browser.selected_index = find_entry_index(listing, selected_entry.name)
    browser._nav_state.adjust_scroll(browser.size.height - 1)
    browser._middle_scroll_offset = browser._nav_state.scroll_offset
    browser._left_scroll_offset = browser._nav_state.get_parent_scroll_offset()


def refresh_panes(browser: FileBrowser) -> None:
    """Refresh all three panes after navigation state changes.

    This function syncs state from NavigationState, refreshes all
    directory listings, and triggers a visual refresh. It should
    be called after any navigation action that changes pane contents.

    Args:
        browser: The file browser instance.
    """
    sync_from_nav_state(browser)
    refresh_listings(browser)
    adjust_left_pane_scroll(browser, browser.size.height - 1)
    adjust_right_pane_scroll(browser, browser.size.height - 1)
    browser.refresh()
