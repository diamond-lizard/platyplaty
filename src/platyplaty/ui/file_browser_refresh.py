"""Refresh functions for the file browser widget.

This module provides functions for refreshing directory listings and
syncing state in the file browser. These are package-private functions
used by the FileBrowser class.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from platyplaty.ui.directory import list_directory
from platyplaty.ui.directory_types import DirectoryEntry, DirectoryListing, EntryType
from platyplaty.ui.file_browser_types import (
    RightPaneContent,
    RightPaneDirectory,
    RightPaneFilePreview,
    read_file_preview_lines,
)

if TYPE_CHECKING:
    from platyplaty.ui.file_browser import FileBrowser


def refresh_listings(browser: FileBrowser) -> None:
    """Refresh all directory listings based on current state.

    Args:
        browser: The file browser instance.
    """
    # Middle pane: current directory
    browser._middle_listing = list_directory(browser.current_dir)

    # Left pane: parent directory (empty at filesystem root)
    parent = browser.current_dir.parent
    if parent == browser.current_dir:
        # At filesystem root
        browser._left_listing = DirectoryListing(
            entries=[],
            was_empty=True,
            had_filtered_entries=False,
            permission_denied=False,
        )
    else:
        browser._left_listing = list_directory(parent)

    # Right pane: preview of selected item
    refresh_right_pane(browser)


def refresh_right_pane(browser: FileBrowser) -> None:
    """Refresh the right pane based on selected item.

    Args:
        browser: The file browser instance.
    """
    if not browser._middle_listing or not browser._middle_listing.entries:
        browser._right_content = None
        return

    if (browser.selected_index < 0
            or browser.selected_index >= len(browser._middle_listing.entries)):
        browser._right_content = None
        return

    selected = browser._middle_listing.entries[browser.selected_index]

    # Only show directory contents for directories
    if selected.entry_type in (EntryType.DIRECTORY, EntryType.SYMLINK_TO_DIRECTORY):
        selected_path = browser.current_dir / selected.name
        browser._right_content = RightPaneDirectory(list_directory(selected_path))
    else:
        # File selected - show file preview
        browser._right_content = make_file_preview(browser, selected)


def make_file_preview(browser: FileBrowser, entry: DirectoryEntry) -> RightPaneContent:
    """Create file preview content for an entry.

    Args:
        browser: The file browser instance.
        entry: The directory entry to preview.

    Returns:
        RightPaneFilePreview with file lines, or None if unreadable.
    """
    file_path = browser.current_dir / entry.name
    lines = read_file_preview_lines(file_path)
    if lines is None:
        return None
    return RightPaneFilePreview(lines)
