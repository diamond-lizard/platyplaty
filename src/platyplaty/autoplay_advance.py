#!/usr/bin/env python3
"""Advance logic for autoplay preset navigation."""

from typing import TYPE_CHECKING

from platyplaty.autoplay_helpers import find_next_playable, try_load_preset

if TYPE_CHECKING:
    from platyplaty.app_context import AppContext
    from platyplaty.playlist import Playlist


async def advance_playlist_to_next(ctx: "AppContext", playlist: "Playlist") -> bool:
    """Advance to the next preset in the playlist.

    Handles looping and skipping of broken presets.

    Args:
        ctx: Application context with client for loading presets.
        playlist: The playlist to advance.

    Returns:
        True if successfully advanced to a playable preset.
    """
    current_index = playlist.get_playing()
    if current_index is None:
        current_index = -1
    next_index = find_next_playable(playlist.presets, current_index)
    if next_index is None:
        return False
    if next_index == current_index:
        return True  # Single-preset playlist, don't reload
    playlist.set_playing(next_index)
    playlist.set_selection(next_index)
    await try_load_preset(ctx, playlist.presets[next_index])
    return True
