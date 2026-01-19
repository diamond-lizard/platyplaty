"""Playlist undo/redo action handlers."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext


async def undo(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Undo the last playlist operation."""
    from platyplaty.playlist_action_helpers import refresh_playlist_view
    from platyplaty.playlist_snapshot import create_snapshot, restore_snapshot
    from platyplaty.ui.playlist_key import (
        is_autoplay_blocking,
        show_autoplay_blocked_error,
    )
    from platyplaty.ui.transient_error import show_transient_error

    if is_autoplay_blocking(ctx):
        await show_autoplay_blocked_error(app)
        return
    undo_mgr = ctx.undo_manager
    if not undo_mgr.can_undo():
        show_transient_error(app, "No further undo information")
        return
    current = create_snapshot(ctx.playlist)
    previous = undo_mgr.undo(current)
    if previous is not None:
        restore_snapshot(ctx.playlist, previous)
        refresh_playlist_view(app)


async def redo(ctx: AppContext, app: PlatyplatyApp) -> None:
    """Redo the last undone playlist operation."""
    from platyplaty.playlist_action_helpers import refresh_playlist_view
    from platyplaty.playlist_snapshot import create_snapshot, restore_snapshot
    from platyplaty.ui.playlist_key import (
        is_autoplay_blocking,
        show_autoplay_blocked_error,
    )
    from platyplaty.ui.transient_error import show_transient_error

    if is_autoplay_blocking(ctx):
        await show_autoplay_blocked_error(app)
        return
    undo_mgr = ctx.undo_manager
    if not undo_mgr.can_redo():
        show_transient_error(app, "No further redo information")
        return
    current = create_snapshot(ctx.playlist)
    next_state = undo_mgr.redo(current)
    if next_state is not None:
        restore_snapshot(ctx.playlist, next_state)
        refresh_playlist_view(app)
