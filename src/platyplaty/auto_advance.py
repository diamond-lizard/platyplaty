#!/usr/bin/env python3
"""Auto-advance and preset loading for Platyplaty.

Handles automatic preset cycling and preset loading with retry logic.
"""

import asyncio
from typing import TYPE_CHECKING

from platyplaty.messages import LogMessage
from platyplaty.socket_client import RendererError

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
        if app._exiting:
            return False
        preset_path = app.playlist.current()
        try:
            await app._client.send_command("LOAD PRESET", path=str(preset_path))
            return True
        except RendererError as e:
            app.post_message(
                LogMessage(f"Failed to load {preset_path}: {e}", level="warning")
            )
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
    consecutive_failures = 0
    max_failures = len(app.playlist.presets)

    try:
        while True:
            if app._exiting:
                break

            # Advance to next preset
            path = app.playlist.next()
            if path is None:
                # At end with loop disabled
                break

            # Try to load the preset
            try:
                success = await _try_load_preset(app)
            except ConnectionError:
                if not app._exiting:
                    app._exiting = True
                    app.exit()
                break

            if success:
                consecutive_failures = 0
                await asyncio.sleep(app.preset_duration)
            else:
                consecutive_failures += 1
                if consecutive_failures >= max_failures:
                    app.post_message(
                        LogMessage("All presets failed to load", level="warning")
                    )
                    break
                await asyncio.sleep(0.5)
    except asyncio.CancelledError:
        pass  # Normal shutdown via Textual worker cancellation



async def _try_load_preset(app: "PlatyplatyApp") -> bool:
    """Try to load the current preset.

    Args:
        app: The Textual application instance.

    Returns:
        True if successful, False otherwise.
    """
    preset_path = app.playlist.current()
    try:
        await app._client.send_command("LOAD PRESET", path=str(preset_path))
        return True
    except RendererError as e:
        app.post_message(
            LogMessage(f"Failed to load {preset_path}: {e}", level="warning")
        )
        return False
