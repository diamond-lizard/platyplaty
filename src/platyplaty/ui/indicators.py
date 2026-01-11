"""Indicator functions for middle pane display.

This module provides functions to calculate and format indicators
for directory entries in the middle pane of the file browser.
Indicators include directory counts, file sizes, and symlink markers.
"""

from pathlib import Path

from platyplaty.ui.directory_entry import get_entry_type, should_include


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
