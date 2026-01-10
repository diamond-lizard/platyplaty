"""Preview content functions for the file browser widget.

This module provides functions for calculating right pane selection
and creating file preview content. These are package-private functions
used by the FileBrowser class.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from platyplaty.ui.file_browser_types import (
    RightPaneContent,
    RightPaneDirectory,
    RightPaneFilePreview,
    read_file_preview_lines,
)

if TYPE_CHECKING:
    from platyplaty.ui.directory_types import DirectoryEntry
    from platyplaty.ui.file_browser import FileBrowser


def calc_right_selection(browser: FileBrowser, dir_path: str) -> int:
    """Calculate the selected index for the right pane directory.

    Args:
        browser: The file browser instance.
        dir_path: The directory path being displayed in right pane.

    Returns:
        The remembered index, or 0 if not found.
    """
    remembered_name = browser._nav_state.get_selected_name_for_directory(dir_path)
    if remembered_name is None:
        return 0
    content = browser._right_content
    if content is None or not isinstance(content, RightPaneDirectory):
        return 0
    listing = content.listing
    if not listing or not listing.entries:
        return 0
    gen = (i for i, e in enumerate(listing.entries) if e.name == remembered_name)
    return next(gen, 0)


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
