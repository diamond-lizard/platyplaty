"""Rendering logic for playlist view widget."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.segment import Segment
from rich.style import Style
from textual.strip import Strip

if TYPE_CHECKING:
    from platyplaty.ui.playlist_view import PlaylistView

# Color constants for playlist items
NORMAL_FG = "white"
NORMAL_BG = "black"
SELECTED_FG = "black"
SELECTED_BG = "white"
DIMMED_FG = "bright_black"
EMPTY_MESSAGE = "No presets in playlist"
PLAYING_PREFIX = "* "
NORMAL_PREFIX = "  "


def render_line(widget: PlaylistView, y: int) -> Strip:
    """Render a single line of the playlist.

    Args:
        widget: The playlist view widget.
        y: The line index within the visible area.

    Returns:
        A Strip representing the rendered line.
    """
    playlist = widget._playlist
    if not playlist.presets:
        return _render_empty_line(widget, y)
    return _render_preset_line(widget, y)


def _render_empty_line(widget: PlaylistView, y: int) -> Strip:
    """Render a line for an empty playlist."""
    width = widget.size.width
    if y == 0:
        style = Style(color=DIMMED_FG, bgcolor=NORMAL_BG)
        text = EMPTY_MESSAGE[:width].ljust(width)
        return Strip([Segment(text, style)])
    return Strip([Segment(" " * width, Style(bgcolor=NORMAL_BG))])


def _render_preset_line(widget: PlaylistView, y: int) -> Strip:
    """Render a line showing a preset entry."""
    index = widget._scroll_offset + y
    presets = widget._playlist.presets
    if index >= len(presets):
        return _render_blank_line(widget)
    return _render_entry(widget, index)


def _render_blank_line(widget: PlaylistView) -> Strip:
    """Render a blank line below the last preset."""
    width = widget.size.width
    return Strip([Segment(" " * width, Style(bgcolor=NORMAL_BG))])


def _render_entry(widget: PlaylistView, index: int) -> Strip:
    """Render a single playlist entry."""
    from platyplaty.ui.playlist_entry_render import render_entry

    return render_entry(widget, index)
