"""Playlist page navigation action handlers.

This module provides page navigation actions (Page Up/Down).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext


async def page_up(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Move selection up by one page (visible height)."""
    from platyplaty.ui.playlist_key import is_autoplay_blocking
    from platyplaty.ui.playlist_key import show_autoplay_blocked_error
    from platyplaty.ui.playlist_view import PlaylistView
    from platyplaty.playlist_action_helpers import refresh_playlist_view

    if is_autoplay_blocking(ctx):
        await show_autoplay_blocked_error(app)
        return
    playlist = ctx.playlist
    if not playlist.presets:
        return
    current = playlist.get_selection()
    if current == 0:
        return
    try:
        view = app.query_one(PlaylistView)
        page_size = max(1, view.size.height)
    except Exception:
        page_size = 1
    new_index = max(0, current - page_size)
    playlist.set_selection(new_index)
    refresh_playlist_view(app)


async def page_down(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Move selection down by one page (visible height)."""
    from platyplaty.ui.playlist_key import is_autoplay_blocking
    from platyplaty.ui.playlist_key import show_autoplay_blocked_error
    from platyplaty.ui.playlist_view import PlaylistView
    from platyplaty.playlist_action_helpers import refresh_playlist_view

    if is_autoplay_blocking(ctx):
        await show_autoplay_blocked_error(app)
        return
    playlist = ctx.playlist
    if not playlist.presets:
        return
    current = playlist.get_selection()
    last_index = len(playlist.presets) - 1
    if current == last_index:
        return
    try:
        view = app.query_one(PlaylistView)
        page_size = max(1, view.size.height)
    except Exception:
        page_size = 1
    new_index = min(last_index, current + page_size)
    playlist.set_selection(new_index)
    refresh_playlist_view(app)

