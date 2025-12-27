#!/usr/bin/env python3
"""Reconnection logic for Platyplaty.

Handles reconnection to the renderer after DISCONNECT events or socket EOF.
For MVP, reconnection re-runs the full startup sequence (CHANGE AUDIO SOURCE,
INIT, LOAD PRESET, SHOW WINDOW) with the renderer handling idempotency.
"""

import contextlib
from typing import TextIO

from platyplaty.event_loop import EventLoopState
from platyplaty.playlist import Playlist
from platyplaty.socket_client import RendererError, SocketClient


async def attempt_reconnect(
    client: SocketClient,
    socket_path: str,
    audio_source: str,
    playlist: Playlist,
    fullscreen: bool,
    state: EventLoopState,
    output: TextIO,
) -> bool:
    """Attempt to reconnect to the renderer and re-run startup sequence.

    Re-runs the full startup sequence: CHANGE AUDIO SOURCE, INIT,
    LOAD PRESET, SHOW WINDOW. The renderer handles idempotency
    (returns "already initialized" for INIT if already initialized).

    Args:
        client: The socket client.
        socket_path: Path to the Unix domain socket.
        audio_source: Audio source for CHANGE AUDIO SOURCE command.
        playlist: The playlist manager (uses current position).
        fullscreen: Whether to enable fullscreen after showing window.
        state: Shared event loop state.
        output: Output stream for status messages.

    Returns:
        True if reconnection succeeded, False otherwise.
    """
    if state.quit_received:
        return False

    try:
        await client.connect(socket_path)
    except OSError as e:
        output.write(f"Reconnect failed: {e}\n")
        output.flush()
        return False

    return await _run_startup_sequence(
        client, audio_source, playlist, fullscreen, output
    )


async def _run_startup_sequence(
    client: SocketClient,
    audio_source: str,
    playlist: Playlist,
    fullscreen: bool,
    output: TextIO,
) -> bool:
    """Run the startup sequence after reconnection.

    Args:
        client: The connected socket client.
        audio_source: Audio source for CHANGE AUDIO SOURCE command.
        playlist: The playlist manager (uses current position).
        fullscreen: Whether to enable fullscreen after showing window.
        output: Output stream for status messages.

    Returns:
        True if startup sequence succeeded, False otherwise.
    """
    try:
        await _send_audio_source(client, audio_source)
        await _send_init(client)
        await _load_current_preset(client, playlist, output)
        await _show_window(client, fullscreen)
        return True
    except (OSError, ConnectionError) as e:
        output.write(f"Startup sequence failed: {e}\n")
        output.flush()
        return False


async def _send_audio_source(
    client: SocketClient,
    audio_source: str,
) -> None:
    """Send CHANGE AUDIO SOURCE command, ignoring expected errors.

    The 'cannot change audio source after INIT' error is expected
    during reconnect per MVP reconnection behavior.

    Args:
        client: The socket client.
        audio_source: Audio source name.
    """
    with contextlib.suppress(RendererError):
        await client.send_command("CHANGE AUDIO SOURCE", source=audio_source)


async def _send_init(client: SocketClient) -> None:
    """Send INIT command, ignoring 'already initialized' error.

    The 'already initialized' error is expected during reconnect
    per MVP reconnection behavior.

    Args:
        client: The socket client.
    """
    with contextlib.suppress(RendererError):
        await client.send_command("INIT")


async def _load_current_preset(
    client: SocketClient,
    playlist: Playlist,
    output: TextIO,
) -> None:
    """Load the current preset from the playlist.

    Args:
        client: The socket client.
        playlist: The playlist manager.
        output: Output stream for warnings.
    """
    preset_path = playlist.current()
    try:
        await client.send_command("LOAD PRESET", path=str(preset_path))
    except RendererError as e:
        output.write(f"Warning: Failed to load {preset_path}: {e}\n")
        output.flush()


async def _show_window(
    client: SocketClient,
    fullscreen: bool,
) -> None:
    """Send SHOW WINDOW command and optionally SET FULLSCREEN.

    Args:
        client: The socket client.
        fullscreen: Whether to enable fullscreen.
    """
    await client.send_command("SHOW WINDOW")
    if fullscreen:
        with contextlib.suppress(RendererError):
            await client.send_command("SET FULLSCREEN", enabled=True)
