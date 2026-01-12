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
    RightPaneEmpty,
    RightPaneNoMilk,
    RightPaneBinaryFile,
    read_file_preview_lines,
    BinaryFileError,
)

from platyplaty.ui.directory_types import EntryType
from platyplaty.ui.directory import list_directory

if TYPE_CHECKING:
    from platyplaty.ui.directory_types import DirectoryEntry
    from platyplaty.ui.file_browser import FileBrowser


FILE_SIZE_LIMIT = 10 * 1024 * 1024  # 10 MB

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
    # Check file size: empty or too large files trigger collapsed state
    try:
        file_size = file_path.stat().st_size
    except OSError:
        return None
    if file_size == 0 or file_size > FILE_SIZE_LIMIT:
        return None
    # Read file content, handling race conditions (file vanished after listing)
    try:
        lines = read_file_preview_lines(file_path)
    except (PermissionError, FileNotFoundError):
        return None
    except BinaryFileError:
        return RightPaneBinaryFile()
    if lines is None:
        return None
    return RightPaneFilePreview(lines)


def get_right_pane_content(
    browser: FileBrowser, selected_entry: DirectoryEntry | None
) -> RightPaneContent:
    """Determine what content to show in the right pane.

    Args:
        browser: The file browser instance.
        selected_entry: The currently selected entry, or None.

    Returns:
        The appropriate RightPaneContent type, or None for collapsed state.
    """
    if selected_entry is None:
        return None
    entry_type = selected_entry.entry_type
    # Broken symlink: collapsed state
    if entry_type == EntryType.BROKEN_SYMLINK:
        return None
    # Directory or symlink to directory
    if entry_type in (EntryType.DIRECTORY, EntryType.SYMLINK_TO_DIRECTORY):
        dir_path = browser.current_dir / selected_entry.name
        listing = list_directory(dir_path)
        if listing.permission_denied:
            return None
        if listing.was_empty:
            return RightPaneEmpty()
        if listing.had_filtered_entries and not listing.entries:
            return RightPaneNoMilk()
        return RightPaneDirectory(listing)
    # File or symlink to file
    if entry_type in (EntryType.FILE, EntryType.SYMLINK_TO_FILE):
        return make_file_preview(browser, selected_entry)
    # Unknown entry type: collapsed state
    return None
