#!/usr/bin/env python3
"""Auto-advance and preset loading for Platyplaty.

Handles automatic preset cycling and preset loading with retry logic.
"""

import asyncio
from contextlib import suppress
from typing import TYPE_CHECKING

from platyplaty.preset_loading import _run_advance_loop, _try_load_preset

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp


async def load_preset_with_retry(app: "PlatyplatyApp") -> bool:
    """Attempt to load the current preset, trying next on failure.

    Tries to load the current playlist preset. On failure, advances
    to the next preset and retries. Gives up if all presets fail.

    Args:
        app: The Textual application instance.

    Returns:
        True if a preset was loaded successfully, False if all failed.
    """
    for _ in range(len(app.playlist.presets)):
        if app._exiting or not app._client:
            return False
        if await _try_load_preset(app):
            return True
        if app.playlist.next() is None:
            break
    return False



async def auto_advance_loop(app: "PlatyplatyApp") -> None:
    """Run the auto-advance loop for preset cycling.

    Runs as a Textual worker. Uses CancelledError for shutdown.
    Advances through playlist, attempting to load each preset.
    On success, waits preset_duration seconds. On failure, waits
    0.5 seconds and retries. Exits if all presets fail consecutively.

    Args:
        app: The Textual application instance.
    """
    max_failures = len(app.playlist.presets)
    with suppress(asyncio.CancelledError):
        await _run_advance_loop(app, max_failures)

