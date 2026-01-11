"""File size formatting functions.

This module provides functions to format file sizes for display
using base-2 units (B, K, M, G, T).
"""

import os
from pathlib import Path


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
