"""Entry rendering functions for file browser panes.

This module provides functions for rendering individual directory entries
with normal or selected (inverted) styling. These are package-private functions.
"""

from rich.segment import Segment
from rich.style import Style

from platyplaty.ui.colors import (
    BACKGROUND_COLOR,
    get_entry_color,
    get_inverted_colors,
)
from platyplaty.ui.directory_types import DirectoryEntry
from platyplaty.ui.indicators import count_directory_contents, format_indicator
from platyplaty.ui.truncation_entry import truncate_entry


def _get_indicator_value(entry_type, path):
    """Get indicator value in format expected by truncate_entry."""
    if entry_type.name == "DIRECTORY":
        return count_directory_contents(path)
    return format_indicator(entry_type, path)


def render_normal_entry(
    entry: DirectoryEntry, width: int, show_indicators: bool = True
) -> list[Segment]:
    """Render an entry with normal (non-selected) colors and 1-char indent."""
    bg_style = Style(bgcolor=BACKGROUND_COLOR)
    color = get_entry_color(entry.entry_type)
    fg_style = Style(color=color, bgcolor=BACKGROUND_COLOR)
    # Reserve 1 char left and right for alignment with selected items
    content_width = max(0, width - 2)
    if show_indicators:
        indicator = _get_indicator_value(entry.entry_type, entry.path)
    else:
        indicator = None
    display_text = truncate_entry(
        entry.name, entry.entry_type, indicator, content_width, show_indicators
    )
    content_text = display_text.ljust(content_width)
    # Build segments: left space + content + right space
    segments = []
    if width > 0:
        segments.append(Segment(" ", bg_style))  # Left indent
    if content_width > 0:
        segments.append(Segment(content_text, fg_style))
    if width > 1:
        segments.append(Segment(" ", bg_style))  # Right space
    return segments


def render_selected_entry(
    entry: DirectoryEntry, width: int, show_indicators: bool = True
) -> list[Segment]:
    """Render an entry with inverted (selected) colors and padding."""
    fg, bg = get_inverted_colors(entry.entry_type)
    style = Style(color=fg, bgcolor=bg)
    # Reserve 1 char left and right for selection padding
    content_width = max(0, width - 2)
    if show_indicators:
        indicator = _get_indicator_value(entry.entry_type, entry.path)
    else:
        indicator = None
    display_text = truncate_entry(
        entry.name, entry.entry_type, indicator, content_width, show_indicators
    )
    content_text = display_text.ljust(content_width)
    # Build segments: left pad + content + right pad (all highlighted)
    segments = []
    if width > 0:
        segments.append(Segment(" ", style))  # Left padding
    if content_width > 0:
        segments.append(Segment(content_text, style))
    if width > 1:
        segments.append(Segment(" ", style))  # Right padding
    return segments
