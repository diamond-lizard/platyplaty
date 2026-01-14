"""Truncation utilities for entries with indicators (middle pane).

This module provides functions to truncate file, directory, and symlink
names when they are displayed with right-justified indicators in the
middle pane. The indicator (size, count, or symlink arrow) is always
preserved except at extreme widths.
"""

from platyplaty.ui.truncation import split_filename, truncate_simple
from platyplaty.ui.truncation_filename import (
    truncate_filename_no_extension,
    truncate_filename_with_extension,
)


def truncate_file_with_indicator(name: str, size_str: str, width: int) -> str:
    """Truncate a file name with preserved size indicator for middle pane.

    The size indicator is right-justified and always preserved unless width
    is too small for even the minimum display. The file name is truncated
    first using file extension rules.

    Args:
        name: The filename (e.g., "cool-preset.milk").
        size_str: The formatted size string (e.g., "1.5 K", "512 B").
        width: Total available width in characters.

    Returns:
        Formatted string with name, padding, and right-justified size.
        Examples:
        - "cool-preset.milk   1.5 K" (fits)
        - "cool-pre~.milk   1.5 K" (name truncated)
        - "v~~ 1.5 K" (minimum with extension)
        - "v~ 512 B" (minimum without extension)

    Edge cases:
        - If width < minimum (len(size_str) + 4 for files with ext,
          len(size_str) + 3 for files without), drop size indicator
          and clamp name to width
        - If width < 2, return first char or empty string
    """
    base, ext = split_filename(name)
    has_ext = bool(ext)

    # Minimum name size: 3 chars for files with extension (v~~), 2 for without (v~)
    min_name_len = 3 if has_ext else 2
    size_len = len(size_str)

    # Minimum total width needed: min_name + 1 space + size
    min_width = min_name_len + 1 + size_len

    # Edge case: width too small for minimum display with indicator
    if width < min_width:
        # Drop indicator, clamp name to width
        if has_ext:
            return truncate_filename_with_extension(base, ext, width)
        return truncate_filename_no_extension(name, width)

    # Calculate available space for name
    # Layout: name + padding (at least 1 space) + size
    name_available = width - 1 - size_len  # -1 for minimum space

    # Truncate name if needed
    if len(name) <= name_available:
        truncated_name = name
    elif has_ext:
        truncated_name = truncate_filename_with_extension(base, ext, name_available)
    else:
        truncated_name = truncate_filename_no_extension(name, name_available)

    # Calculate padding to right-justify the size
    padding = width - len(truncated_name) - size_len

    return truncated_name + (" " * padding) + size_str


def truncate_directory(name: str, count: int, width: int) -> str:
    """Truncate a directory name with preserved count indicator for middle pane.

    The count indicator is right-justified and always preserved unless width
    is too small for even the minimum display. The directory name is truncated
    using simple right truncation with tilde.

    Args:
        name: The directory name.
        count: The directory entry count (integer).
        width: Total available width in characters.

    Returns:
        Formatted string with name, padding, and right-justified count.
        Examples:
        - "presets   42" (fits)
        - "pres~   42" (name truncated)
        - "v~ 42" (minimum display)

    Edge cases:
        - If width < minimum (len(count_str) + 3), drop count indicator
          and clamp name to width
        - If width < 2, return first char or empty string
    """
    count_str = str(count)
    count_len = len(count_str)

    # Minimum name size: 2 chars (first letter + tilde)
    min_name_len = 2

    # Minimum total width needed: min_name + 1 space + count
    min_width = min_name_len + 1 + count_len

    # Edge case: width too small for minimum display with indicator
    if width < min_width:
        # Drop indicator, clamp name to width
        return truncate_simple(name, width)

    # Calculate available space for name
    # Layout: name + padding (at least 1 space) + count
    name_available = width - 1 - count_len  # -1 for minimum space

    # Truncate name if needed
    if len(name) <= name_available:
        truncated_name = name
    else:
        truncated_name = truncate_simple(name, name_available)

    # Calculate padding to right-justify the count
    padding = width - len(truncated_name) - count_len

    return truncated_name + (" " * padding) + count_str
