"""Playlist delete action handler."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext


async def delete_from_playlist(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Delete selected preset from playlist."""
    from platyplaty.playlist_action_helpers import (
        load_preset_at_index,
        refresh_playlist_view,
    )
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
    was_playing = playing == current
    playlist.remove_preset(current)
    if not playlist.presets:
        playlist.set_selection(0)
        playlist.set_playing(None)
        refresh_playlist_view(app)
        return
    new_selection = min(current, len(playlist.presets) - 1)
    playlist.set_selection(new_selection)
    if was_playing:
        playlist.set_playing(new_selection)
        await load_preset_at_index(ctx, new_selection)
    elif playing is not None and playing > current:
        playlist.set_playing(playing - 1)
    refresh_playlist_view(app)
