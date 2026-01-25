"""Entry rendering functions for file browser panes.

This module provides functions for rendering individual directory entries
with normal or selected (inverted) styling. These are package-private functions.
"""

from pathlib import Path

from rich.segment import Segment
from rich.style import Style

from platyplaty.bad_presets import is_preset_bad
from platyplaty.ui.colors import (
    BACKGROUND_COLOR,
    BAD_PRESET_BG,
    BAD_PRESET_FG,
    DIMMED_COLOR,
    get_entry_color,
    get_inverted_colors,
)
from platyplaty.ui.directory_types import DirectoryEntry, EntryType
from platyplaty.ui.indicators import count_directory_contents, format_indicator
from platyplaty.ui.truncation_entry import truncate_entry


def _get_indicator_value(entry_type: EntryType, path: Path) -> int | str:
    """Get indicator value in format expected by truncate_entry."""
    if entry_type.name == "DIRECTORY":
        return count_directory_contents(path)
    return format_indicator(entry_type, path)


def _is_bad_preset(entry: DirectoryEntry) -> bool:
    """Check if entry is a preset file that has crashed the renderer."""
    if entry.entry_type not in (EntryType.FILE, EntryType.SYMLINK_TO_FILE):
        return False
    return is_preset_bad(entry.path)


def render_normal_entry(
    entry: DirectoryEntry, width: int, show_indicators: bool = True,
    focused: bool = True
) -> list[Segment]:
    """Render an entry with normal (non-selected) colors and 1-char indent."""
    if focused and _is_bad_preset(entry):
        fg_style = Style(color=BAD_PRESET_FG, bgcolor=BAD_PRESET_BG)
        bg_style = Style(bgcolor=BAD_PRESET_BG)
    else:
        bg_style = Style(bgcolor=BACKGROUND_COLOR)
        color = get_entry_color(entry.entry_type) if focused else DIMMED_COLOR
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
    entry: DirectoryEntry, width: int, show_indicators: bool = True,
    focused: bool = True
) -> list[Segment]:
    """Render an entry with inverted (selected) colors and padding."""
    if focused:
        if _is_bad_preset(entry):
            fg, bg = BAD_PRESET_BG, BAD_PRESET_FG
        else:
            fg, bg = get_inverted_colors(entry.entry_type)
        style = Style(color=fg, bgcolor=bg)
    else:
        style = Style(color=DIMMED_COLOR, bgcolor=BACKGROUND_COLOR)
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
