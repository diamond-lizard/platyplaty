"""Playlist jump navigation action handlers.

This module provides Home/End navigation actions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext


async def navigate_to_first_preset(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Move selection to first preset in playlist."""
    from platyplaty.ui.playlist_key import is_autoplay_blocking
    from platyplaty.ui.playlist_key import show_autoplay_blocked_error
    from platyplaty.playlist_action_helpers import refresh_playlist_view

    if is_autoplay_blocking(ctx):
        await show_autoplay_blocked_error(app)
        return
    playlist = ctx.playlist
    if not playlist.presets:
        return
    if playlist.get_selection() == 0:
        return
    playlist.set_selection(0)
    refresh_playlist_view(app)


async def navigate_to_last_preset(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Move selection to last preset in playlist."""
    from platyplaty.ui.playlist_key import is_autoplay_blocking
    from platyplaty.ui.playlist_key import show_autoplay_blocked_error
    from platyplaty.playlist_action_helpers import refresh_playlist_view

    if is_autoplay_blocking(ctx):
        await show_autoplay_blocked_error(app)
        return
    playlist = ctx.playlist
    if not playlist.presets:
        return
    last_index = len(playlist.presets) - 1
    if playlist.get_selection() == last_index:
        return
    playlist.set_selection(last_index)
    refresh_playlist_view(app)
