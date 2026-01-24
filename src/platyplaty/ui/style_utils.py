#!/usr/bin/env python3
"""Utility functions for Rich style manipulation."""

from rich.style import Style


def reverse_style(style: Style) -> Style:
    """Swap foreground and background colors of a style.

    Args:
        style: The style to reverse.

    Returns:
        A new Style with color and bgcolor swapped.
        If either is None, it remains None (not swapped).
    """
    fg = style.color
    bg = style.bgcolor
    return Style(color=bg, bgcolor=fg)
