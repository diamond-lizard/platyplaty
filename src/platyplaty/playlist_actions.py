"""Playlist action handlers for the Platyplaty application.

This module provides async action handlers for playlist keyboard events.
These are invoked by the app's action_* methods.
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
    playlist = ctx.playlist
    if not playlist.presets:
        return
    current = playlist.get_selection()
    new_index = current + delta
    if new_index < 0 or new_index >= len(playlist.presets):
        return
    playlist.set_selection(new_index)
    _refresh_playlist_view(app)


def _refresh_playlist_view(app: PlatyplatyApp) -> None:
    """Refresh the playlist view widget."""
    from platyplaty.ui.playlist_view import PlaylistView

    try:
        view = app.query_one(PlaylistView)
        view.notify_playlist_changed()
    except Exception:
        pass

async def play_next(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Play next preset (selection and playing indicator move together)."""
    from platyplaty.ui.playlist_key import is_autoplay_blocking, show_autoplay_blocked_error

    if is_autoplay_blocking(ctx):
        await show_autoplay_blocked_error(app)
        return
    await _play_by_delta(ctx, app, 1)


async def play_previous(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Play previous preset (selection and playing indicator move together)."""
    from platyplaty.ui.playlist_key import is_autoplay_blocking, show_autoplay_blocked_error

    if is_autoplay_blocking(ctx):
        await show_autoplay_blocked_error(app)
        return
    await _play_by_delta(ctx, app, -1)


async def _play_by_delta(ctx: AppContext, app: PlatyplatyApp, delta: int) -> None:
    """Move selection and playing indicator by delta, then load preset."""
    from platyplaty.autoplay_helpers import try_load_preset

    playlist = ctx.playlist
    if not playlist.presets:
        return
    current = playlist.get_selection()
    new_index = current + delta
    if new_index < 0 or new_index >= len(playlist.presets):
        return
    playlist.set_selection(new_index)
    playlist.set_playing(new_index)
    _refresh_playlist_view(app)
    await try_load_preset(ctx, playlist.presets[new_index])


async def reorder_up(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Move selected preset up in the playlist."""
    from platyplaty.ui.playlist_key import is_autoplay_blocking, show_autoplay_blocked_error

    if is_autoplay_blocking(ctx):
        await show_autoplay_blocked_error(app)
        return
    playlist = ctx.playlist
    if not playlist.presets:
        return
    current = playlist.get_selection()
    if playlist.move_preset_up(current):
        playlist.set_selection(current - 1)
        _refresh_playlist_view(app)


async def reorder_down(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Move selected preset down in the playlist."""
    from platyplaty.ui.playlist_key import is_autoplay_blocking, show_autoplay_blocked_error

    if is_autoplay_blocking(ctx):
        await show_autoplay_blocked_error(app)
        return
    playlist = ctx.playlist
    if not playlist.presets:
        return
    current = playlist.get_selection()
    if playlist.move_preset_down(current):
        playlist.set_selection(current + 1)
        _refresh_playlist_view(app)


async def delete_from_playlist(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Delete selected preset from playlist."""
    from platyplaty.ui.playlist_key import is_autoplay_blocking, show_autoplay_blocked_error

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
        _refresh_playlist_view(app)
        return
    new_selection = min(current, len(playlist.presets) - 1)
    playlist.set_selection(new_selection)
    if was_playing:
        playlist.set_playing(new_selection)
        await _load_preset_at_index(ctx, new_selection)
    elif playing is not None and playing > current:
        playlist.set_playing(playing - 1)
    _refresh_playlist_view(app)


async def _load_preset_at_index(ctx: AppContext, index: int) -> None:
    """Load the preset at the given index."""
    from platyplaty.autoplay_helpers import try_load_preset

    playlist = ctx.playlist
    if 0 <= index < len(playlist.presets):
        await try_load_preset(ctx, playlist.presets[index])


async def undo(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Undo the last playlist operation."""
    from platyplaty.playlist_snapshot import create_snapshot, restore_snapshot
    from platyplaty.ui.transient_error import show_transient_error

    undo_mgr = ctx.undo_manager
    if not undo_mgr.can_undo():
        show_transient_error(app, "No further undo information")
        return
    current = create_snapshot(ctx.playlist)
    previous = undo_mgr.undo(current)
    if previous is not None:
        restore_snapshot(ctx.playlist, previous)
        _refresh_playlist_view(app)


async def redo(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Redo the last undone playlist operation."""
    from platyplaty.playlist_snapshot import create_snapshot, restore_snapshot
    from platyplaty.ui.transient_error import show_transient_error

    undo_mgr = ctx.undo_manager
    if not undo_mgr.can_redo():
        show_transient_error(app, "No further redo information")
        return
    current = create_snapshot(ctx.playlist)
    next_state = undo_mgr.redo(current)
    if next_state is not None:
        restore_snapshot(ctx.playlist, next_state)
        _refresh_playlist_view(app)


async def play_selection(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Play the currently selected preset in the playlist."""
    from platyplaty.ui.playlist_key import is_autoplay_blocking, show_autoplay_blocked_error
    from platyplaty.autoplay_helpers import try_load_preset

    if is_autoplay_blocking(ctx):
        await show_autoplay_blocked_error(app)
        return
    playlist = ctx.playlist
    if not playlist.presets:
        return
    current = playlist.get_selection()
    playlist.set_playing(current)
    _refresh_playlist_view(app)
    await try_load_preset(ctx, playlist.presets[current])


async def open_selected(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Open the currently selected preset in $EDITOR."""
    from platyplaty.ui.editor import open_in_editor

    playlist = ctx.playlist
    if not playlist.presets:
        return
    current = playlist.get_selection()
    preset_path = playlist.presets[current]
    await open_in_editor(app, preset_path)


async def page_up(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Move selection up by one page (visible height)."""
    from platyplaty.ui.playlist_key import is_autoplay_blocking, show_autoplay_blocked_error
    from platyplaty.ui.playlist_view import PlaylistView

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
    _refresh_playlist_view(app)


async def page_down(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Move selection down by one page (visible height)."""
    from platyplaty.ui.playlist_key import is_autoplay_blocking, show_autoplay_blocked_error
    from platyplaty.ui.playlist_view import PlaylistView

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
    _refresh_playlist_view(app)


async def navigate_to_first_preset(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Move selection to first preset in playlist."""
    from platyplaty.ui.playlist_key import is_autoplay_blocking, show_autoplay_blocked_error

    if is_autoplay_blocking(ctx):
        await show_autoplay_blocked_error(app)
        return
    playlist = ctx.playlist
    if not playlist.presets:
        return
    if playlist.get_selection() == 0:
        return
    playlist.set_selection(0)
    _refresh_playlist_view(app)


async def navigate_to_last_preset(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Move selection to last preset in playlist."""
    from platyplaty.ui.playlist_key import is_autoplay_blocking, show_autoplay_blocked_error

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
    _refresh_playlist_view(app)


async def shuffle_playlist(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Shuffle the playlist in place."""
    if ctx.current_focus != "playlist":
        return
    playlist = ctx.playlist
    if len(playlist.presets) < 2:
        return
    from platyplaty.playlist_snapshot import push_undo_snapshot
    push_undo_snapshot(ctx)
    playlist.shuffle()
    _refresh_playlist_view(app)
