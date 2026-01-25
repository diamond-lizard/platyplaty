"""Shared helper functions for playlist actions."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext
    from platyplaty.playlist import Playlist


def refresh_playlist_view(app: PlatyplatyApp) -> None:
    """Refresh the playlist view widget."""
    from platyplaty.ui.playlist_view import PlaylistView

    try:
        view = app.query_one(PlaylistView)
        view.notify_playlist_changed()
    except Exception:
        pass


async def load_preset_at_index(ctx: AppContext, app: PlatyplatyApp, index: int) -> None:
    """Load the preset at the given index."""
    from platyplaty.preset_command import load_preset

    playlist = ctx.playlist
    if 0 <= index < len(playlist.presets):
        await load_preset(ctx, app, playlist.presets[index])


def scroll_playlist_to_playing(app: PlatyplatyApp) -> None:
    """Scroll the playlist view to make the playing preset visible."""
    from platyplaty.ui.playlist_scroll import scroll_to_playing
    from platyplaty.ui.playlist_view import PlaylistView

    try:
        view = app.query_one(PlaylistView)
        scroll_to_playing(view, view.size.height)
        view.refresh()
    except Exception:
        pass


def find_preset_index(playlist: Playlist, path: Path) -> int | None:
    """Find the index of a preset in the playlist.

    If preset appears multiple times, prefer current playing index.
    Otherwise return first instance.

    Args:
        playlist: The playlist to search.
        path: Path to the preset.

    Returns:
        Index of the preset, or None if not in playlist.
    """
    indices = [i for i, p in enumerate(playlist.presets) if p == path]
    if not indices:
        return None
    playing = playlist.get_playing()
    if playing in indices:
        return playing
    return indices[0]


async def autoplay_first_preset(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Load and play the first preset in the playlist."""
    playlist = ctx.playlist
    playlist.set_selection(0)
    playlist.set_playing(0)
    await load_preset_at_index(ctx, app, 0)
