#!/usr/bin/env python3
"""Timer loop helpers for autoplay functionality."""

import asyncio
from contextlib import suppress
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.autoplay_manager import AutoplayManager


async def run_timer_loop(manager: "AutoplayManager") -> None:
    """Run the autoplay timer loop.

    Args:
        manager: The autoplay manager instance.
    """
    with suppress(asyncio.CancelledError):
        await _run_autoplay_cycle(manager)


async def _run_autoplay_cycle(manager: "AutoplayManager") -> None:
    """Execute the autoplay cycle until disabled or cancelled.

    Args:
        manager: The autoplay manager instance.
    """
    while manager.autoplay_enabled and await _wait_and_advance(manager):
        pass


async def _wait_and_advance(manager: "AutoplayManager") -> bool:
    """Wait for preset_duration then advance.

    Args:
        manager: The autoplay manager instance.

    Returns:
        False if autoplay disabled or no playable presets found.
    """
    await asyncio.sleep(manager.preset_duration)
    if not manager.autoplay_enabled:
        return False
    if not await manager.advance_to_next():
        manager.stop_autoplay_with_error()
        return False
    return True
