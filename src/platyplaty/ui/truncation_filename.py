"""Filename truncation utilities for the file browser.

This module provides functions to truncate file names when they are
too long to fit within pane widths. Handles both files with extensions
(multi-stage truncation) and files without extensions (simple truncation).
"""

from platyplaty.ui.truncation import truncate_simple


def truncate_filename_with_extension(name: str, ext: str, width: int) -> str:
    """Truncate a filename with extension using multi-stage rules.

    Stages:
        1. If name + ext fits, return as-is
        2. Truncate base name, add tilde before extension (e.g., base~.ext)
        3. Continue truncating base to minimum 1 char + tilde + extension
        4. Truncate extension with tilde (e.g., v~.ex~)
        5. Absolute minimum: 3 chars (v~~) - first letter, tilde, tilde

    Args:
        name: The base name of the file (without extension).
        ext: The extension including the dot (e.g., ".milk").
        width: Maximum width in characters.

    Returns:
        The truncated filename. Edge cases for width < 3 are handled
        gracefully (width=2 returns first char + tilde, width=1 returns
        first char, width=0 returns empty string).
    """
    full = name + ext
    # Edge cases for very small widths
    if width <= 0:
        return ""
    if width == 1:
        return name[0] if name else (ext[0] if ext else "~")
    if width == 2:
        return (name[0] if name else (ext[0] if ext else "~")) + "~"
    # Stage 1: If it fits, return as-is
    if len(full) <= width:
        return full
    # Stage 2-3: Truncate base name, keep extension
    # Need space for: truncated_base + "~" + ext
    # Minimum base is 1 char, so minimum is: 1 + 1 + len(ext) = 2 + len(ext)
    if width >= 2 + len(ext):
        base_width = width - 1 - len(ext)  # -1 for tilde
        return name[:base_width] + "~" + ext
    # Stage 4: Truncate extension with tilde
    # Format: first_char + "~" + "." + truncated_ext + "~"
    # Minimum is 4 chars: v~.e~  (but we can go to v~~ at width=3)
    if width >= 4:
        # v~ + . + ext chars + ~
        ext_width = width - 3  # -2 for "v~", -1 for trailing "~"
        return (name[0] if name else "~") + "~" + ext[:ext_width] + "~"
    # Stage 5: Absolute minimum (width == 3)
    # Return v~~ (first char + tilde for base + tilde for ext, dot omitted)
    return (name[0] if name else (ext[1] if len(ext) > 1 else "~")) + "~~"


def truncate_filename_no_extension(name: str, width: int) -> str:
    """Truncate a filename without extension using simple right truncation.

    For files without extensions, truncate from the right with a single tilde.
    Minimum is 2 characters (first letter + tilde).

    Args:
        name: The filename (without extension).
        width: Maximum width in characters.

    Returns:
        The truncated filename. Edge cases:
        - width=0: returns empty string
        - width=1: returns first char (or tilde if name is empty)
        - If name fits: returns as-is
        - If name too long: returns first (width-1) chars + tilde
    """
    return truncate_simple(name, width)
