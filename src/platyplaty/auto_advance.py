#!/usr/bin/env python3
"""Auto-advance and preset loading for Platyplaty.

Handles automatic preset cycling and preset loading with retry logic.
"""

import asyncio
from pathlib import Path
from typing import TextIO

from platyplaty.event_loop import EventLoopState
from platyplaty.playlist import Playlist
from platyplaty.socket_client import RendererError, SocketClient


async def load_preset_with_retry(
    client: SocketClient,
    playlist: Playlist,
    output: TextIO,
) -> bool:
    """Attempt to load the current preset, trying next on failure.

    Args:
        client: The socket client.
        playlist: The playlist manager.
        output: Output stream for warnings.

    Returns:
        True if a preset was loaded successfully, False if all failed.
    """
    attempts = 0
    max_attempts = len(playlist.presets)

    while attempts < max_attempts:
        preset_path = playlist.current()
        try:
            await client.send_command("LOAD PRESET", path=str(preset_path))
            return True
        except RendererError as e:
            msg = f"Warning: Failed to load {preset_path}: {e}\n"
            output.write(msg)
            output.flush()
            attempts += 1
            next_preset = playlist.next()
            if next_preset is None:
                break

    return False


async def auto_advance_loop(
    client: SocketClient,
    playlist: Playlist,
    duration: int,
    state: EventLoopState,
    output: TextIO,
) -> None:
    """Run the auto-advance loop for preset cycling.

    Args:
        client: The socket client.
        playlist: The playlist manager.
        duration: Seconds between preset changes.
        state: Shared event loop state.
        output: Output stream for warnings.
    """
    while not state.shutdown_requested:
        try:
            await asyncio.sleep(duration)
        except asyncio.CancelledError:
            break

        if state.shutdown_requested:
            break

        if playlist.at_end() and not playlist.loop:
            break

        next_preset = playlist.next()
        if next_preset is None:
            break

        try:
            await _try_load_preset(client, next_preset, output)
        except ConnectionError:
            state.disconnect_event.set()
            break


async def _try_load_preset(
    client: SocketClient,
    preset_path: Path,
    output: TextIO,
) -> bool:
    """Try to load a single preset.

    Args:
        client: The socket client.
        preset_path: Path to the preset file.
        output: Output stream for warnings.

    Returns:
        True if successful, False otherwise.
    """
    try:
        await client.send_command("LOAD PRESET", path=str(preset_path))
        return True
    except RendererError as e:
        msg = f"Warning: Failed to load {preset_path}: {e}\n"
        output.write(msg)
        output.flush()
        return False
