#!/usr/bin/env python3
"""Functions for starting autoplay and loading the first preset."""

from typing import TYPE_CHECKING

from platyplaty.autoplay_errors import show_no_playable_error
from platyplaty.preset_command import load_preset

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext
    from platyplaty.playlist import Playlist


async def load_first_preset(
    ctx: "AppContext", app: "PlatyplatyApp", playlist: "Playlist", first_index: int
) -> bool:
    """Load the first playable preset and handle errors.

    Args:
        ctx: Application context with client.
        playlist: The playlist to operate on.
        first_index: Index of the first playable preset.

    Returns:
        True if a preset was successfully loaded, False otherwise.
    """
    preset_path = playlist.presets[first_index]
    success, error = await load_preset(ctx, app, preset_path)
    if success or error is None:
        return success
    playlist.broken_indices.add(first_index)
    ctx.error_log.append(error)
    return await try_advance_after_error(ctx, app, playlist)


async def try_advance_after_error(
    ctx: "AppContext", app: "PlatyplatyApp", playlist: "Playlist"
) -> bool:
    """Try to advance to the next playable preset after an error.

    Args:
        ctx: Application context.
        playlist: The playlist to advance.

    Returns:
        True if advanced to a playable preset, False if no more playable presets.
    """
    from platyplaty.autoplay_advance import advance_playlist_to_next
    return await advance_playlist_to_next(ctx, app, playlist)


def handle_start_failure(app: "PlatyplatyApp") -> None:
    """Handle failure to start autoplay.

    Args:
        app: The Textual application instance.
    """
    show_no_playable_error(app)


async def start_from_first_preset(
    ctx: "AppContext", app: "PlatyplatyApp", playlist: "Playlist"
) -> bool:
    """Find the first playable preset and start playing it.

    Sets selection and playing indices before loading.

    Args:
        ctx: Application context with client.
        playlist: The playlist to operate on.

    Returns:
        True if a preset was found and loaded, False otherwise.
    """
    from platyplaty.autoplay_helpers import find_next_playable
    first_playable = find_next_playable(playlist, -1)
    if first_playable is None:
        return False
    playlist.set_playing(first_playable)
    playlist.set_selection(first_playable)
    return await load_first_preset(ctx, app, playlist, first_playable)
