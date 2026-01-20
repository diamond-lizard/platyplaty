"""Playlist edit action handlers.

This module provides edit actions (reorder, shuffle, save).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext



async def shuffle_playlist(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Shuffle the playlist in place."""
    from platyplaty.playlist_action_helpers import refresh_playlist_view
    from platyplaty.playlist_snapshot import push_undo_snapshot

    if ctx.current_focus != "playlist":
        return
    playlist = ctx.playlist
    if len(playlist.presets) < 2:
        return
    selected_path = playlist.presets[playlist.get_selection()]
    playing_idx = playlist.get_playing()
    playing_path = playlist.presets[playing_idx] if playing_idx is not None else None
    push_undo_snapshot(ctx)
    playlist.shuffle()
    playlist.set_selection(playlist.presets.index(selected_path))
    if playing_path is not None:
        playlist.set_playing(playlist.presets.index(playing_path))
    refresh_playlist_view(app)


async def save_playlist(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Save playlist to associated filename."""
    from platyplaty.playlist_action_helpers import refresh_playlist_view
    from platyplaty.playlist_persistence import save_to_file
    from platyplaty.ui.transient_error import show_transient_error

    playlist = ctx.playlist
    if playlist.associated_filename is None:
        show_transient_error(app, "Error: No file name")
        return
    try:
        save_to_file(playlist)
    except OSError as e:
        show_transient_error(app, f"Error: could not save playlist: {e}")
        return
    refresh_playlist_view(app)
