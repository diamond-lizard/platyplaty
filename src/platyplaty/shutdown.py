#!/usr/bin/env python3
"""Signal handling and graceful shutdown for Platyplaty.

Provides signal handler registration and shutdown coordination
for the async event loop.
"""

import asyncio
import contextlib
import signal

from platyplaty.event_loop import EventLoopState
from platyplaty.socket_client import SocketClient


def register_signal_handlers(
    loop: asyncio.AbstractEventLoop,
    state: EventLoopState,
) -> None:
    """Register signal handlers for graceful shutdown.

    Registers handlers for SIGINT (Ctrl+C) and SIGTERM that set
    the shutdown_requested flag.

    Args:
        loop: The asyncio event loop.
        state: Shared event loop state to set shutdown flag.
    """
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _signal_handler, state)


def _signal_handler(state: EventLoopState) -> None:
    """Handle shutdown signals.

    Sets the shutdown flag so the event loop can send QUIT safely.

    Args:
        state: Shared event loop state.
    """
    state.shutdown_requested = True


async def send_quit_command(client: SocketClient) -> bool:
    """Send QUIT command to renderer and wait for response.

    Args:
        client: The socket client.

    Returns:
        True if QUIT was acknowledged, False on error.
    """
    try:
        await client.send_command("QUIT")
        return True
    except Exception:  # noqa: BLE001
        return False


async def graceful_shutdown(client: SocketClient) -> None:
    """Perform graceful shutdown: send QUIT and close socket.

    Sends the QUIT command to the renderer, waits for the response,
    then closes the socket connection.

    Args:
        client: The socket client to close.
    """
    try:
        await send_quit_command(client)
    finally:
        client.close()


async def cancel_tasks(tasks: list[asyncio.Task[object]]) -> None:
    """Cancel a list of asyncio tasks and wait for them to finish.

    Args:
        tasks: List of tasks to cancel.
    """
    for task in tasks:
        if not task.done():
            task.cancel()

    for task in tasks:
        with contextlib.suppress(asyncio.CancelledError):
            await task
