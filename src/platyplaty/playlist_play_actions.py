"""Playlist playback action handlers.

This module provides playback actions (J/K, ENTER, toggle_autoplay).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext


async def play_next(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Play next preset (selection and playing indicator move together)."""
    from platyplaty.ui.playlist_key import (
        is_autoplay_blocking,
        show_autoplay_blocked_error,
    )

    if is_autoplay_blocking(ctx):
        await show_autoplay_blocked_error(app)
        return
    await _play_by_delta(ctx, app, 1)


async def play_previous(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Play previous preset (selection and playing indicator move together)."""
    from platyplaty.ui.playlist_key import (
        is_autoplay_blocking,
        show_autoplay_blocked_error,
    )

    if is_autoplay_blocking(ctx):
        await show_autoplay_blocked_error(app)
        return
    await _play_by_delta(ctx, app, -1)


async def _play_by_delta(ctx: AppContext, app: PlatyplatyApp, delta: int) -> None:
    """Move selection and playing indicator by delta, then load preset."""
    from platyplaty.autoplay_helpers import try_load_preset
    from platyplaty.playlist_action_helpers import refresh_playlist_view

    playlist = ctx.playlist
    if not playlist.presets:
        return
    current = playlist.get_selection()
    new_index = current + delta
    if new_index < 0 or new_index >= len(playlist.presets):
        return
    playlist.set_selection(new_index)
    playlist.set_playing(new_index)
    refresh_playlist_view(app)
    await try_load_preset(ctx, playlist.presets[new_index])


async def play_selection(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Play the currently selected preset in the playlist."""
    from platyplaty.autoplay_helpers import try_load_preset
    from platyplaty.playlist_action_helpers import refresh_playlist_view
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
    playlist.set_playing(current)
    refresh_playlist_view(app)
    await try_load_preset(ctx, playlist.presets[current])


async def toggle_autoplay(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Toggle autoplay on or off."""
    from platyplaty.playlist_action_helpers import refresh_playlist_view

    if ctx.current_focus != "playlist":
        return
    autoplay_mgr = ctx.autoplay_manager
    if autoplay_mgr is None:
        return
    await autoplay_mgr.toggle_autoplay()
    refresh_playlist_view(app)


async def open_selected(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Open the currently selected preset in $EDITOR."""
    from platyplaty.ui.editor import open_in_editor

    playlist = ctx.playlist
    if not playlist.presets:
        return
    current = playlist.get_selection()
    preset_path = playlist.presets[current]
    await open_in_editor(app, preset_path)
