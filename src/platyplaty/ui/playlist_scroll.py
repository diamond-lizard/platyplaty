"""Scroll adjustment for playlist view widget.

Uses the Safe-Zone Scroll Algorithm to keep the selection visible.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from platyplaty.ui.nav_scroll import calc_safe_zone_scroll

if TYPE_CHECKING:
    from platyplaty.ui.playlist_view import PlaylistView


def adjust_scroll(widget: PlaylistView, pane_height: int) -> None:
    """Adjust scroll offset so the selected item is visible.

    Uses the Safe-Zone Scroll Algorithm from nav_scroll.

    Args:
        widget: The playlist view widget.
        pane_height: The height of the pane in lines.
    """
    if pane_height <= 0:
        return
    playlist = widget._playlist
    if not playlist.presets:
        widget._scroll_offset = 0
        return
    selected_index = playlist.get_selection()
    item_count = len(playlist.presets)
    widget._scroll_offset = calc_safe_zone_scroll(
        selected_index,
        widget._scroll_offset,
        pane_height,
        item_count,
    )


def scroll_to_playing(widget: PlaylistView, pane_height: int) -> None:
    """Scroll to make the playing preset visible.

    Uses the Safe-Zone Scroll Algorithm from nav_scroll.

    Args:
        widget: The playlist view widget.
        pane_height: The height of the pane in lines.
    """
    if pane_height <= 0:
        return
    playlist = widget._playlist
    playing_index = playlist.get_playing()
    if playing_index is None:
        return
    if not playlist.presets:
        return
    item_count = len(playlist.presets)
    widget._scroll_offset = calc_safe_zone_scroll(
        playing_index,
        widget._scroll_offset,
        pane_height,
        item_count,
    )
