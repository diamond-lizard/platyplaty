#!/usr/bin/env python3
"""Preset loading command with crash tracking.

This module provides the send_load_preset function which tracks the preset
path before sending the LOAD PRESET command. This tracking enables crash
detection to identify which preset caused a renderer crash.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app_context import AppContext
    from platyplaty.app import PlatyplatyApp


async def send_load_preset(ctx: AppContext, path: Path | str) -> None:
    """Send LOAD PRESET command with crash tracking.

    This function sets ctx.preset_sent_to_renderer before sending the
    command. This allows crash detection code to identify which preset
    caused the renderer to crash.

    All code that loads presets should use load_preset() (added in Phase
    600) instead of calling this function directly. This function is
    internal infrastructure for crash tracking.

    Args:
        ctx: Application context with client for sending commands.
        path: Preset file path (Path) or special URL like "idle://" (str).
    """
    ctx.preset_sent_to_renderer = path
    assert ctx.client is not None, "Client must exist before loading preset"
    await ctx.client.send_command("LOAD PRESET", path=str(path))


async def load_preset(
    ctx: AppContext,
    app: "PlatyplatyApp",
    path: Path | str,
) -> tuple[bool, str | None]:
    """Load a preset into the renderer with automatic restart.
    
    This is the main entry point for loading presets. It handles:
    1. Skipping bad/missing presets (for file paths)
    2. Restarting the renderer if it has crashed
    3. Crash tracking via send_load_preset
    4. Showing window and setting fullscreen on success
    
    Args:
        ctx: Application context with renderer state.
        app: The Textual application instance.
        path: Preset file path (Path) or special URL like "idle://" (str).
    
    Returns:
        Tuple of (success, error_message). error_message is None on success,
        validation failure, or renderer start failure; contains renderer
        error message on load failure.
    """
    from platyplaty.autoplay_helpers import is_preset_playable
    from platyplaty.renderer_restart import ensure_renderer_running
    from platyplaty.socket_exceptions import RendererError
    
    # For file presets, check if playable (skip bad/missing)
    if isinstance(path, Path) and not is_preset_playable(path):
        return (False, None)
    
    # Ensure renderer is running (restart if crashed)
    if not await ensure_renderer_running(ctx, app):
        return (False, None)
    
    # Send the load command with crash tracking
    try:
        await send_load_preset(ctx, path)
    except (RendererError, ConnectionError) as e:
        return (False, str(e))
    
    # Show window and set fullscreen on success
    await ctx.client.send_command("SHOW WINDOW")
    if ctx.config.fullscreen:
        await ctx.client.send_command("SET FULLSCREEN", enabled=True)
    
    return (True, None)
