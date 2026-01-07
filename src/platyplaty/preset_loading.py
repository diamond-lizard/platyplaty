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


async def _process_one_advance_step(
    app: "PlatyplatyApp", consecutive_failures: int, max_failures: int
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
    path = app.playlist.next()
    if path is None:
        return ("break", consecutive_failures, 0.0)

    try:
        success = await _try_load_preset(app)
    except ConnectionError:
        if not app._exiting:
            app._exiting = True
            app.exit()
        return ("break", consecutive_failures, 0.0)

    if success:
        return ("sleep", 0, app.preset_duration)

    new_failures = consecutive_failures + 1
    if new_failures >= max_failures:
        app.post_message(
            LogMessage("All presets failed to load", level="warning")
        )
        return ("break", new_failures, 0.0)
    return ("sleep", new_failures, 0.5)


async def _run_advance_loop(
    app: "PlatyplatyApp", max_failures: int
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
        if app._exiting:
            break
        action, consecutive_failures, sleep_time = await _process_one_advance_step(
            app, consecutive_failures, max_failures
        )
        if action == "break":
            break
        await asyncio.sleep(sleep_time)


async def _try_load_preset(app: "PlatyplatyApp") -> bool:
    """Try to load the current preset.

    Args:
        app: The Textual application instance.

    Returns:
        True if successful, False otherwise.
    """
    preset_path = app.playlist.current()
    if not app._client:
        return False
    try:
        await app._client.send_command("LOAD PRESET", path=str(preset_path))
        return True
    except RendererError as e:
        app.post_message(
            LogMessage(f"Failed to load {preset_path}: {e}", level="warning")
        )
        return False
