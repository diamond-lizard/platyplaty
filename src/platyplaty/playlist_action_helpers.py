"""Shared helper functions for playlist actions."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext


def refresh_playlist_view(app: PlatyplatyApp) -> None:
    """Refresh the playlist view widget."""
    from platyplaty.ui.playlist_view import PlaylistView

    try:
        view = app.query_one(PlaylistView)
        view.notify_playlist_changed()
    except Exception:
        pass


async def load_preset_at_index(ctx: AppContext, index: int) -> None:
    """Load the preset at the given index."""
    from platyplaty.autoplay_helpers import try_load_preset

    playlist = ctx.playlist
    if 0 <= index < len(playlist.presets):
        await try_load_preset(ctx, playlist.presets[index])
