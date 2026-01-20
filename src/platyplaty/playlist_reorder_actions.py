"""Playlist reorder action handlers.

This module provides reorder actions (move up, move down).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext


async def reorder_up(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Move selected preset up in the playlist."""
    from platyplaty.playlist_action_helpers import refresh_playlist_view
    from platyplaty.playlist_snapshot import push_undo_snapshot
    from platyplaty.ui.playlist_key import (
        is_autoplay_blocking,
        show_autoplay_blocked_error,
    )

    if is_autoplay_blocking(ctx):
        await show_autoplay_blocked_error(app)
        return
    playlist = ctx.playlist
    if not playlist.presets:
        return
    current = playlist.get_selection()
    playing = playlist.get_playing()
    push_undo_snapshot(ctx)
    if playlist.move_preset_up(current):
        playlist.set_selection(current - 1)
        if playing == current:
            playlist.set_playing(current - 1)
        elif playing == current - 1:
            playlist.set_playing(current)
        refresh_playlist_view(app)


async def reorder_down(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Move selected preset down in the playlist."""
    from platyplaty.playlist_action_helpers import refresh_playlist_view
    from platyplaty.playlist_snapshot import push_undo_snapshot
    from platyplaty.ui.playlist_key import (
        is_autoplay_blocking,
        show_autoplay_blocked_error,
    )

    if is_autoplay_blocking(ctx):
        await show_autoplay_blocked_error(app)
        return
    playlist = ctx.playlist
    if not playlist.presets:
        return
    current = playlist.get_selection()
    playing = playlist.get_playing()
    push_undo_snapshot(ctx)
    if playlist.move_preset_down(current):
        playlist.set_selection(current + 1)
        if playing == current:
            playlist.set_playing(current + 1)
        elif playing == current + 1:
            playlist.set_playing(current)
        refresh_playlist_view(app)
