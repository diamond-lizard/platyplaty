#!/usr/bin/env python3
"""Preset loading helpers for auto-advance.

Helper functions for loading presets during auto-advance cycling.
"""

import asyncio
from typing import TYPE_CHECKING

from platyplaty.messages import LogMessage
from platyplaty.socket_exceptions import RendererError

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext


async def _process_one_advance_step(
    ctx: "AppContext",
    app: "PlatyplatyApp",
    consecutive_failures: int,
    max_failures: int,
) -> tuple[str, int, float]:
    """Process one step of auto-advance.

    Args:
        app: The Textual application instance.
        consecutive_failures: Current failure count.
        max_failures: Maximum allowed consecutive failures.

    Returns:
        Tuple of (action, new_failure_count, sleep_time).
        Action is "break" or "sleep".
    """
    path = ctx.playlist.next()
    if path is None:
        return ("break", consecutive_failures, 0.0)

    try:
        success = await _try_load_preset(ctx, app)
    except ConnectionError:
        if not ctx.exiting:
            ctx.exiting = True
            app.exit()
        return ("break", consecutive_failures, 0.0)

    if success:
        return ("sleep", 0, ctx.config.preset_duration)

    new_failures = consecutive_failures + 1
    if new_failures >= max_failures:
        app.post_message(
            LogMessage("All presets failed to load", level="warning")
        )
        return ("break", new_failures, 0.0)
    return ("sleep", new_failures, 0.5)


async def _run_advance_loop(
    ctx: "AppContext", app: "PlatyplatyApp", max_failures: int
) -> None:
    """Run the inner advance loop.

    Loops through presets, loading each and sleeping between advances.
    Exits when app is exiting, playlist ends, or all presets fail.

    Args:
        app: The Textual application instance.
        max_failures: Maximum consecutive failures before giving up.
    """
    consecutive_failures = 0
    while True:
        if ctx.exiting:
            break
        action, consecutive_failures, sleep_time = await _process_one_advance_step(
            ctx, app, consecutive_failures, max_failures
        )
        if action == "break":
            break
        await asyncio.sleep(sleep_time)


async def _try_load_preset(ctx: "AppContext", app: "PlatyplatyApp") -> bool:
    """Try to load the current preset.

    Args:
        app: The Textual application instance.

    Returns:
        True if successful, False otherwise.
    """
    preset_path = ctx.playlist.current()
    if not ctx.client:
        return False
    try:
        await ctx.client.send_command("LOAD PRESET", path=str(preset_path))
        return True
    except RendererError as e:
        app.post_message(
            LogMessage(f"Failed to load {preset_path}: {e}", level="warning")
        )
        return False
