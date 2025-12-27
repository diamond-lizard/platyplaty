#!/usr/bin/env python3
"""Event loop state and stderr monitoring for Platyplaty.

Provides shared state for event loop tasks and monitors renderer stderr
for PLATYPLATY events (DISCONNECT, AUDIO_ERROR, QUIT).
"""

import asyncio
from typing import TextIO

from platyplaty.stderr_parser import (
    StderrEvent,
    StderrEventType,
    log_audio_error,
    parse_stderr_event,
)


class EventLoopState:
    """Shared state for the event loop tasks.

    Attributes:
        shutdown_requested: Set to True to request graceful shutdown.
        quit_received: Set to True when QUIT event received (no reconnect).
        disconnect_event: Set when DISCONNECT event received (reconnect).
    """

    shutdown_requested: bool
    quit_received: bool
    disconnect_event: asyncio.Event
    shutdown_event: asyncio.Event

    def __init__(self) -> None:
        """Initialize event loop state."""
        self.shutdown_requested = False
        self.quit_received = False
        self.disconnect_event = asyncio.Event()
        self.shutdown_event = asyncio.Event()


async def process_stderr_line(
    line: str,
    state: EventLoopState,
    output: TextIO,
) -> None:
    """Process a single stderr line, detecting PLATYPLATY events.

    Args:
        line: The stderr line to process.
        state: Shared event loop state.
        output: Output stream for non-event lines.
    """
    event = parse_stderr_event(line)
    if event is None:
        output.write(line)
        output.flush()
        return

    _handle_stderr_event(event, state, output)


def _handle_stderr_event(
    event: StderrEvent,
    state: EventLoopState,
    output: TextIO,
) -> None:
    """Handle a parsed PLATYPLATY stderr event.

    Args:
        event: The parsed event.
        state: Shared event loop state.
        output: Output stream for logging.
    """
    if event.event == StderrEventType.QUIT:
        state.quit_received = True
        state.shutdown_requested = True
        state.shutdown_event.set()
    elif event.event == StderrEventType.DISCONNECT:
        state.disconnect_event.set()
    elif event.event == StderrEventType.AUDIO_ERROR:
        log_audio_error(event)


async def stderr_monitor_task(
    process: asyncio.subprocess.Process,
    state: EventLoopState,
    output: TextIO,
) -> None:
    """Monitor renderer stderr for events.

    Args:
        process: The renderer subprocess.
        state: Shared event loop state.
        output: Output stream for passthrough.
    """
    if process.stderr is None:
        return

    async for line_bytes in process.stderr:
        line = line_bytes.decode()
        await process_stderr_line(line, state, output)
        if state.shutdown_requested:
            break

    # Renderer process exited - trigger shutdown
    state.shutdown_event.set()
