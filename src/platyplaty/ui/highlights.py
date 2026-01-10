#!/usr/bin/env python3
"""Highlight bounds calculation for selection highlighting.

This module provides functions to calculate padding for selection
highlights in the file browser panes.
"""


def calc_highlight_bounds(content_length: int, pane_width: int) -> tuple[int, int]:
    """Calculate left and right padding for selection highlight.

    The highlight extends 1 character left and right of the displayed
    content, clamped to stay within pane bounds.

    Args:
        content_length: Length of the displayed content in characters.
        pane_width: Width of the pane in characters.

    Returns:
        A tuple of (left_padding, right_padding) in characters.
    """
    if pane_width <= 0 or content_length <= 0:
        return (0, 0)
    available = pane_width - content_length
    if available <= 0:
        return (0, 0)
    left_pad = min(1, available)
    right_pad = min(1, available - left_pad)
    return (left_pad, right_pad)
