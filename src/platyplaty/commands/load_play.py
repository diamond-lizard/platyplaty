#!/usr/bin/env python3
"""Functions for playing presets after a playlist load."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext


async def play_after_load(ctx: "AppContext", app: "PlatyplatyApp") -> None:
    """Start playing after a playlist load.

    Handles:
    - Empty playlist: set to idle (playing_index = None)
    - Non-empty playlist: play first playable preset
    - Autoplay running: continue with new playlist, restart timer

    Args:
        ctx: Application context.
        app: The Textual application.
    """
    playlist = ctx.playlist
    if not playlist.presets:
        playlist.set_playing(None)
        return
    await play_first_preset(ctx, app)
    handle_autoplay_continuation(ctx)


async def play_first_preset(ctx: "AppContext", app: "PlatyplatyApp") -> None:
    """Play the first playable preset in the playlist.

    Args:
        ctx: Application context.
        app: The Textual application.
    """
    from platyplaty.autoplay_start import start_from_first_preset
    await start_from_first_preset(ctx, ctx.playlist)


def handle_autoplay_continuation(ctx: "AppContext") -> None:
    """Handle autoplay continuation after load.

    If autoplay is running, restart the timer for the new playlist.

    Args:
        ctx: Application context.
    """
    if ctx.autoplay_manager is None:
        return
    if not ctx.autoplay_manager.autoplay_enabled:
        return
    ctx.autoplay_manager._start_timer()
