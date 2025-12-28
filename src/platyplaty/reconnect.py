#!/usr/bin/env python3
"""Reconnection logic for Platyplaty.

Handles reconnection to the renderer after DISCONNECT events or socket EOF.
Uses GET STATUS to query current state and sends only commands needed to
synchronize (LOAD PRESET, SHOW WINDOW, SET FULLSCREEN) based on differences.
"""

from typing import TextIO

from platyplaty.event_loop import EventLoopState
from platyplaty.playlist import Playlist
from platyplaty.socket_client import RendererError, SocketClient
from platyplaty.types import StatusData


async def attempt_reconnect(
    client: SocketClient,
    socket_path: str,
    playlist: Playlist,
    fullscreen: bool,
    state: EventLoopState,
    output: TextIO,
) -> bool:
    """Attempt to reconnect to the renderer and re-run startup sequence.

    Uses GET STATUS to query current renderer state and sends only
    the commands needed to synchronize (LOAD PRESET, SHOW WINDOW,
    SET FULLSCREEN) based on differences from desired state.

    Args:
        client: The socket client.
        socket_path: Path to the Unix domain socket.
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

    return await _sync_state_from_status(
        client, playlist, fullscreen, output
    )


async def _sync_state_from_status(
    client: SocketClient,
    playlist: Playlist,
    fullscreen: bool,
    output: TextIO,
) -> bool:
    """Synchronize client state with renderer using GET STATUS.

    Queries renderer state and sends only the commands needed to
    synchronize. Skips redundant commands based on current state.

    Args:
        client: The connected socket client.
        playlist: The playlist manager (uses current position).
        fullscreen: Desired fullscreen state.
        output: Output stream for status messages.

    Returns:
        True if GET STATUS succeeds and sync commands complete.
        False if GET STATUS fails or critical sync commands fail.
        Note: audio_connected=false is a warning, not a failure.
    """
    # Query current renderer state
    try:
        response = await client.send_command("GET STATUS")
    except (RendererError, ConnectionError):
        return False

    status = StatusData.model_validate(response.data)

    # Warn if audio is disconnected
    if not status.audio_connected:
        output.write(
            "Warning: Audio disconnected, visualization may be "
            "unresponsive to music\n"
        )
        output.flush()

    # Load preset if different from current
    current_preset = str(playlist.current())
    if status.preset_path != current_preset:
        try:
            await client.send_command("LOAD PRESET", path=current_preset)
        except (RendererError, ConnectionError):
            return False

    # Show window if not visible
    if not status.visible:
        try:
            await client.send_command("SHOW WINDOW")
        except (RendererError, ConnectionError):
            return False

    # Set fullscreen if different from desired
    if status.fullscreen != fullscreen:
        try:
            await client.send_command("SET FULLSCREEN", enabled=fullscreen)
        except (RendererError, ConnectionError):
            return False

    return True
