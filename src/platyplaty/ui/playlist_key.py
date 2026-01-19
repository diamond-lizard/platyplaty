"""Key handling functions for the playlist section.

This module provides action handler functions for playlist keyboard events.
Actions are dispatched via the playlist dispatch table when playlist is focused.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext


def is_autoplay_blocking(ctx: AppContext) -> bool:
    """Check if autoplay is blocking navigation/editing keys."""
    autoplay_mgr = getattr(ctx, "autoplay_manager", None)
    if autoplay_mgr is None:
        return False
    return autoplay_mgr.autoplay_enabled


async def show_autoplay_blocked_error(app: PlatyplatyApp) -> None:
    """Show error message for blocked key during autoplay."""
    from platyplaty.ui.transient_error import show_transient_error

    show_transient_error(app, "Turn off autoplay first")


def get_playlist_selection(ctx: AppContext) -> int | None:
    """Get current playlist selection index, or None if empty."""
    playlist = ctx.playlist
    if not playlist.presets:
        return None
    return playlist.get_selection()
