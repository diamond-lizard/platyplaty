#!/usr/bin/env python3
"""Advance logic for autoplay preset navigation."""

from typing import TYPE_CHECKING

from platyplaty.autoplay_errors import is_renderer_connection_error
from platyplaty.autoplay_helpers import find_next_playable
from platyplaty.playlist_action_helpers import refresh_playlist_view
from platyplaty.preset_command import load_preset

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext
    from platyplaty.playlist import Playlist


async def advance_playlist_to_next(
    ctx: "AppContext", app: "PlatyplatyApp", playlist: "Playlist"
) -> bool:
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
    next_index = find_next_playable(playlist, current_index)
    if next_index is None:
        return False
    if next_index == current_index:
        return True  # Single-preset playlist, don't reload
    playlist.set_playing(next_index)
    playlist.set_selection(next_index)
    refresh_playlist_view(app)
    success, error = await load_preset(ctx, app, playlist.presets[next_index])
    if not success and error is not None:
        # Don't mark preset as broken if renderer connection is dead.
        # The crash handler will mark the actual crashed preset.
        if is_renderer_connection_error(error):
            ctx.error_log.append(error)
            return False
        playlist.broken_indices.add(next_index)
        ctx.error_log.append(error)
        return await advance_playlist_to_next(ctx, app, playlist)
    return success
