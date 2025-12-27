#!/usr/bin/env python3
"""Async main loop for Platyplaty.

Handles the async portion of startup: renderer connection,
initialization commands, and the main event loop.
"""

import asyncio
from typing import TextIO

from platyplaty.auto_advance import auto_advance_loop, load_preset_with_retry
from platyplaty.event_loop import EventLoopState, stderr_monitor_task
from platyplaty.playlist import Playlist
from platyplaty.renderer import start_renderer
from platyplaty.reconnect import attempt_reconnect
from platyplaty.shutdown import (
    cancel_tasks,
    graceful_shutdown,
    register_signal_handlers,
)
from platyplaty.socket_client import SocketClient


async def async_main(
    socket_path: str,
    audio_source: str,
    playlist: Playlist,
    preset_duration: int,
    fullscreen: bool,
    output: TextIO,
) -> None:
    """Run the async portion of the startup sequence.

    Args:
        socket_path: Path to the Unix domain socket.
        audio_source: PulseAudio source for audio capture.
        playlist: The preset playlist.
        preset_duration: Seconds between preset changes.
        fullscreen: Whether to start in fullscreen mode.
        output: Output stream for status messages.
    """
    # Start renderer subprocess
    renderer_process = await start_renderer(socket_path)

    # Connect to socket
    client = SocketClient()
    await client.connect(socket_path)

    # Send CHANGE AUDIO SOURCE command
    await client.send_command("CHANGE AUDIO SOURCE", source=audio_source)

    # Send INIT command
    await client.send_command("INIT")

    # Attempt to load first preset; try next on failure
    preset_loaded = await load_preset_with_retry(client, playlist, output)
    if not preset_loaded:
        output.write("Warning: All presets failed to load; showing idle preset\n")
        output.flush()

    # Send SHOW WINDOW command
    await client.send_command("SHOW WINDOW")

    # Send SET FULLSCREEN if configured
    if fullscreen:
        await client.send_command("SET FULLSCREEN", enabled=True)

    # Enter main event loop
    state = EventLoopState()
    loop = asyncio.get_event_loop()
    register_signal_handlers(loop, state)

    # Create background tasks
    stderr_task = asyncio.create_task(
        stderr_monitor_task(renderer_process, state, output)
    )
    advance_task = asyncio.create_task(
        auto_advance_loop(client, playlist, preset_duration, state, output)
    )

    try:
        # Main event loop: handle shutdown and disconnect events
        while not state.shutdown_requested:
            shutdown_task = asyncio.create_task(state.shutdown_event.wait())
            disconnect_task = asyncio.create_task(state.disconnect_event.wait())
            done, pending = await asyncio.wait(
                [shutdown_task, disconnect_task],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
            
            if shutdown_task in done:
                break
            
            # Disconnect event: attempt reconnection
            if disconnect_task in done and not state.quit_received:
                await cancel_tasks([advance_task])
                client.close()
                await asyncio.sleep(0.5)
                
                success = await attempt_reconnect(
                    client, socket_path, audio_source, playlist,
                    fullscreen, state, output,
                )
                if not success:
                    output.write("Error: Reconnection failed, exiting\n")
                    output.flush()
                    break
                
                # Restart auto-advance task after successful reconnect
                state.disconnect_event.clear()
                advance_task = asyncio.create_task(
                    auto_advance_loop(
                        client, playlist, preset_duration, state, output
                    )
                )
    finally:
        await cancel_tasks([stderr_task, advance_task])
        await graceful_shutdown(client)
