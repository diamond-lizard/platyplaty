"""Truncation for directories with count indicators (middle pane).

This module provides the function to truncate directory names when they are
displayed with right-justified count indicators in the middle pane.
The count indicator is always preserved except at extreme widths.
"""

from platyplaty.ui.truncation import truncate_simple


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
