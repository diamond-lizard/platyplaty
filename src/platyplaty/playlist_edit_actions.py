"""Playlist edit action handlers.

This module provides edit actions (reorder, shuffle, save).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext


async def reorder_up(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Move selected preset up in the playlist."""
    from platyplaty.ui.playlist_key import is_autoplay_blocking
    from platyplaty.ui.playlist_key import show_autoplay_blocked_error
    from platyplaty.playlist_action_helpers import refresh_playlist_view

    if is_autoplay_blocking(ctx):
        await show_autoplay_blocked_error(app)
        return
    playlist = ctx.playlist
    if not playlist.presets:
        return
    current = playlist.get_selection()
    if playlist.move_preset_up(current):
        playlist.set_selection(current - 1)
        refresh_playlist_view(app)


async def reorder_down(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Move selected preset down in the playlist."""
    from platyplaty.ui.playlist_key import is_autoplay_blocking
    from platyplaty.ui.playlist_key import show_autoplay_blocked_error
    from platyplaty.playlist_action_helpers import refresh_playlist_view

    if is_autoplay_blocking(ctx):
        await show_autoplay_blocked_error(app)
        return
    playlist = ctx.playlist
    if not playlist.presets:
        return
    current = playlist.get_selection()
    if playlist.move_preset_down(current):
        playlist.set_selection(current + 1)
        refresh_playlist_view(app)

async def shuffle_playlist(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Shuffle the playlist in place."""
    from platyplaty.playlist_action_helpers import refresh_playlist_view
    from platyplaty.playlist_snapshot import push_undo_snapshot

    if ctx.current_focus != "playlist":
        return
    playlist = ctx.playlist
    if len(playlist.presets) < 2:
        return
    push_undo_snapshot(ctx)
    playlist.shuffle()
    refresh_playlist_view(app)


async def save_playlist(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Save playlist to associated filename."""
    from platyplaty.ui.transient_error import show_transient_error
    from platyplaty.playlist_persistence import save_to_file
    from platyplaty.playlist_action_helpers import refresh_playlist_view

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
