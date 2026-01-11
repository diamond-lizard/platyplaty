"""Indicator functions for middle pane display.

This module provides functions to calculate and format indicators
for directory entries in the middle pane of the file browser.
Indicators include directory counts, file sizes, and symlink markers.
"""

import os
from pathlib import Path

from platyplaty.ui.directory_entry import get_entry_type, should_include
from platyplaty.ui.directory_types import EntryType


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


def get_file_size(path: Path) -> int:
    """Get file size in bytes using os.stat.

    Args:
        path: Path to the file.

    Returns:
        File size in bytes, or 0 on error (file deleted, permission denied).
    """
    try:
        return os.stat(path).st_size
    except (OSError, PermissionError):
        return 0


def get_symlink_size(path: Path) -> int:
    """Get symlink file size in bytes using os.lstat (does not follow symlinks).

    Args:
        path: Path to the symlink.

    Returns:
        Symlink file size in bytes, or 0 on error.
    """
    try:
        return os.lstat(path).st_size
    except (OSError, PermissionError):
        return 0


def format_file_size(size_bytes: int) -> str:
    """Format file size for display.

    Uses base-2 units (1 K = 1024 bytes).

    Args:
        size_bytes: File size in bytes.

    Returns:
        Formatted size string (e.g., "512 B", "1.5 K", "2 M").
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    return _format_with_unit(size_bytes)


def _format_with_unit(size_bytes: int) -> str:
    """Format size >= 1024 bytes with appropriate unit."""
    units = [("K", 1024), ("M", 1024**2), ("G", 1024**3), ("T", 1024**4)]
    for unit, threshold in reversed(units):
        if size_bytes >= threshold:
            value = size_bytes / threshold
            return _format_value_with_unit(value, unit)
    return f"{size_bytes} B"


def _format_value_with_unit(value: float, unit: str) -> str:
    """Format a value with its unit, removing trailing zeros."""
    formatted = f"{value:.2f}"
    # Remove trailing zeros and decimal point if not needed
    formatted = formatted.rstrip("0").rstrip(".")
    return f"{formatted} {unit}"


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
