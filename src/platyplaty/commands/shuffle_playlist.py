#!/usr/bin/env python3
"""Shuffle playlist command handler.

Implements the :shuffle command for randomizing playlist order.
"""

from pathlib import Path
from typing import TYPE_CHECKING

from platyplaty.playlist_snapshot import push_undo_snapshot

if TYPE_CHECKING:
    from platyplaty.app_context import AppContext
    from platyplaty.playlist import Playlist


async def execute(ctx: "AppContext") -> tuple[bool, str | None]:
    """Execute the :shuffle command.

    Shuffles the playlist in place, preserving which preset is selected
    and which is playing. Does not reset autoplay timer.

    Args:
        ctx: Application context.

    Returns:
        Tuple of (success, error_message). error_message is None on success.
    """
    playlist = ctx.playlist
    if not playlist.presets:
        return (True, None)
    selected_path = playlist.presets[playlist.get_selection()]
    playing_path = get_playing_path(playlist)
    push_undo_snapshot(ctx)
    playlist.shuffle()
    restore_indices(playlist, selected_path, playing_path)
    return (True, None)


def get_playing_path(playlist: "Playlist") -> "Path | None":
    """Get the path of the currently playing preset, if any."""
    playing_idx = playlist.get_playing()
    if playing_idx is None:
        return None
    return playlist.presets[playing_idx]


def restore_indices(
    playlist: "Playlist", selected_path: "Path", playing_path: "Path | None"
) -> None:
    """Restore selection and playing indices after shuffle."""
    new_selection = playlist.presets.index(selected_path)
    playlist.set_selection(new_selection)
    if playing_path is not None:
        new_playing = playlist.presets.index(playing_path)
        playlist.set_playing(new_playing)
