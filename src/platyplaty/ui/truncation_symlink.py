"""Truncation for symlinks with indicators (middle pane).

This module provides the function to truncate symlink names when they are
displayed with right-justified indicators in the middle pane.
The indicator is always preserved except at extreme widths.

Indicator formats:
- "-> 42" for symlinks to directories (count of target directory)
- "-> 1.5 K" for symlinks to files (size of target file)
- "-> 15 B" for broken symlinks (size of symlink file itself)
"""

from platyplaty.ui.truncation import truncate_simple


def truncate_symlink(name: str, indicator: str, width: int) -> str:
    """Truncate a symlink name with preserved indicator for middle pane.

    The indicator is right-justified and always preserved unless width
    is too small for even the minimum display. The symlink name is truncated
    using simple right truncation with tilde.

    Args:
        name: The symlink name.
        indicator: The formatted indicator (e.g., "-> 42", "-> 1.5 K").
        width: Total available width in characters.

    Returns:
        Formatted string with name, padding, and right-justified indicator.
        Examples:
        - "favorites       -> 42" (fits)
        - "favo~       -> 42" (name truncated)
        - "v~ -> 1 K" (minimum display)

    Edge cases:
        - If width < minimum (len(indicator) + 3), drop indicator
          and clamp name to width
        - If width < 2, return first char or empty string
    """
    indicator_len = len(indicator)

    # Minimum name size: 2 chars (first letter + tilde)
    min_name_len = 2

    # Minimum total width needed: min_name + 1 space + indicator
    min_width = min_name_len + 1 + indicator_len

    # Edge case: width too small for minimum display with indicator
    if width < min_width:
        # Drop indicator, clamp name to width
        return truncate_simple(name, width)

    # Calculate available space for name
    # Layout: name + padding (at least 1 space) + indicator
    name_available = width - 1 - indicator_len  # -1 for minimum space

    # Truncate name if needed
    if len(name) <= name_available:
        truncated_name = name
    else:
        truncated_name = truncate_simple(name, name_available)

    # Calculate padding to right-justify the indicator
    padding = width - len(truncated_name) - indicator_len

    return truncated_name + (" " * padding) + indicator
