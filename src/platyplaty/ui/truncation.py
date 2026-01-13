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
