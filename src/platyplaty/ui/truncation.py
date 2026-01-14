"""Truncation utilities for the file browser.

This module provides functions to truncate file and directory names
when they are too long to fit within pane widths. The truncation
uses tilde (~) as the indicator throughout.
"""


def truncate_simple(text: str, width: int) -> str:
    """Truncate text to fit within width using a tilde indicator.

    Args:
        text: The text to truncate.
        width: Maximum width in characters.

    Returns:
        The text if it fits, otherwise truncated with tilde.
        Edge cases:
        - width=0: returns empty string
        - width=1: returns first char (or tilde if text is empty)
        - If text fits: returns as-is
        - If text too long: returns first (width-1) chars + tilde
    """
    if width <= 0:
        return ""
    if width == 1:
        return text[0] if text else "~"
    if len(text) <= width:
        return text
    return text[: width - 1] + "~"


def split_filename(name: str) -> tuple[str, str]:
    """Split a filename into base and extension.

    The extension is the part after the last dot (including the dot).
    If there is no dot, the extension is empty.

    Args:
        name: The filename to split.

    Returns:
        A tuple of (base, extension). For "file.txt" returns ("file", ".txt").
        For "noext" returns ("noext", ""). For ".hidden" returns ("", ".hidden").
    """
    dot_pos = name.rfind(".")
    if dot_pos <= 0:
        return (name, "")
    return (name[:dot_pos], name[dot_pos:])
