"""Indicator functions for middle pane display.

This module provides functions to calculate and format indicators
for directory entries in the middle pane of the file browser.
Indicators include directory counts, file sizes, and symlink markers.
"""

from pathlib import Path

import cachetools

from platyplaty.ui.directory_entry import get_entry_type, should_include
from platyplaty.ui.directory_types import EntryType
from platyplaty.ui.size_format import format_file_size, get_file_size, get_symlink_size

directory_count_cache: cachetools.LRUCache[tuple[Path], int] = (
    cachetools.LRUCache(maxsize=10000)
)


@cachetools.cached(directory_count_cache)
def count_directory_contents(path: Path) -> int:
    """Count filtered directory contents.

    Counts entries that match the visibility filter:
    - Directories (excluding . and ..)
    - .milk files (case-insensitive extension)
    - Symlinks to either of the above
    - Broken symlinks if name ends in .milk or has no extension

    For symlinks to directories, this counts the target directory's
    contents (Path.iterdir follows symlinks).

    Args:
        path: Path to the directory to count.

    Returns:
        Number of entries matching the visibility filter, or 0 if
        the directory is inaccessible.
    """
    try:
        entries = list(path.iterdir())
    except (PermissionError, OSError):
        return 0
    return sum(
        1 for p in entries if should_include(p, get_entry_type(p))
    )


def format_indicator(entry_type: EntryType, path: Path) -> str:
    """Format indicator string for a directory entry.

    Args:
        entry_type: Type of the entry (directory, file, symlink, etc.).
        path: Path to the entry.

    Returns:
        Indicator string (count for directories, size for files,
        arrow prefix with count/size for symlinks).
    """
    if entry_type == EntryType.DIRECTORY:
        return str(count_directory_contents(path))
    if entry_type == EntryType.FILE:
        return format_file_size(get_file_size(path))
    if entry_type == EntryType.SYMLINK_TO_DIRECTORY:
        return f"-> {count_directory_contents(path)}"
    if entry_type == EntryType.SYMLINK_TO_FILE:
        return f"-> {format_file_size(get_file_size(path))}"
    if entry_type == EntryType.BROKEN_SYMLINK:
        return f"-> {format_file_size(get_symlink_size(path))}"
    return ""

