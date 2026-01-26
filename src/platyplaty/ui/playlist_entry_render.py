"""Entry rendering for playlist view widget."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.segment import Segment
from rich.style import Style
from textual.strip import Strip

from platyplaty.ui.truncation import truncate_simple

if TYPE_CHECKING:
    from platyplaty.ui.playlist_view import PlaylistView

PLAYING_PREFIX = "* "
NORMAL_PREFIX = "  "
LEFT_MARGIN = 1
RIGHT_MARGIN = 1


def render_entry(widget: PlaylistView, index: int) -> Strip:
    """Render a single playlist entry with all indicators.

    Args:
        widget: The playlist view widget.
        index: The index of the entry to render.

    Returns:
        A Strip representing the rendered entry.
    """
    width = widget.size.width
    playlist = widget._playlist
    is_selected = index == playlist.get_selection()
    is_playing = index == playlist.get_playing()
    is_focused = widget._focused
    is_broken = index in playlist.broken_indices

    display_name = _get_display_name(widget, index)
    prefix = PLAYING_PREFIX if is_playing else NORMAL_PREFIX
    content_width = width - LEFT_MARGIN - RIGHT_MARGIN - len(prefix)
    truncated_name = truncate_simple(display_name, max(0, content_width))

    style = _get_style(is_selected, is_focused, is_broken)
    text = _build_line(prefix, truncated_name, width)

    return Strip([Segment(text, style)])


def _get_display_name(widget: PlaylistView, index: int) -> str:
    """Get the display name for a preset at the given index."""
    if index < len(widget._display_names):
        return widget._display_names[index]
    return widget._playlist.presets[index].name


def _get_style(is_selected: bool, is_focused: bool, is_broken: bool) -> Style:
    """Get the style for an entry based on selection, focus and broken state."""
    if is_broken:
        if is_selected:
            return Style(color="black", bgcolor="red")
        return Style(color="red", bgcolor="black")
    if is_selected and is_focused:
        return Style(color="black", bgcolor="white")
    if is_selected:
        return Style(color="bright_black", bgcolor="black")
    if not is_focused:
        return Style(color="bright_black", bgcolor="black")
    return Style(color="white", bgcolor="black")


def _build_line(prefix: str, name: str, width: int) -> str:
    """Build the full line with margins, prefix, and name."""
    content = " " * LEFT_MARGIN + prefix + name
    return content.ljust(width)[:width]
