"""Playlist navigation action handlers.

This module provides selection navigation actions (j/k selection movement).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext


async def navigate_up(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Move selection up by one (no play)."""
    from platyplaty.ui.playlist_key import is_autoplay_blocking

    if ctx.current_focus != "playlist":
        return
    if is_autoplay_blocking(ctx):
        from platyplaty.ui.playlist_key import show_autoplay_blocked_error
        await show_autoplay_blocked_error(app)
        return
    _move_selection(ctx, app, -1)


async def navigate_down(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Move selection down by one (no play)."""
    from platyplaty.ui.playlist_key import is_autoplay_blocking

    if ctx.current_focus != "playlist":
        return
    if is_autoplay_blocking(ctx):
        from platyplaty.ui.playlist_key import show_autoplay_blocked_error
        await show_autoplay_blocked_error(app)
        return
    _move_selection(ctx, app, 1)


def _move_selection(ctx: AppContext, app: PlatyplatyApp, delta: int) -> None:
    """Move selection by delta, clamping to bounds."""
    from platyplaty.playlist_action_helpers import refresh_playlist_view

    playlist = ctx.playlist
    if not playlist.presets:
        return
    current = playlist.get_selection()
    new_index = current + delta
    if new_index < 0 or new_index >= len(playlist.presets):
        return
    playlist.set_selection(new_index)
    refresh_playlist_view(app)
