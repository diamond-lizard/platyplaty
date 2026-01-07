#!/usr/bin/env python3
"""Stderr monitoring for Platyplaty.

Monitors renderer stderr for PLATYPLATY events (DISCONNECT, AUDIO_ERROR,
QUIT, KEY_PRESSED).
"""

import asyncio
from typing import TYPE_CHECKING

from platyplaty.keybinding_dispatch import dispatch_key_event
from platyplaty.messages import LogMessage
from platyplaty.netstring import read_netstrings_from_stderr
from platyplaty.stderr_parser import parse_stderr_event
from platyplaty.types import StderrEvent

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp

async def process_stderr_line(
    line: str,
    app: "PlatyplatyApp",
) -> None:
    """Process a single stderr line, detecting PLATYPLATY events.

    Args:
        line: The stderr line to process.
        app: The Textual application instance.
    """
    event = parse_stderr_event(line)
    if event is None:
        app.post_message(LogMessage(line.rstrip(), level="debug"))
        return

    await _handle_stderr_event(event, app)


async def _handle_stderr_event(
    event: StderrEvent,
    app: "PlatyplatyApp",
) -> None:
    """Handle a parsed PLATYPLATY stderr event.

    Args:
        event: The parsed event.
        app: The Textual application instance.
    """
    if event.event == "QUIT" or event.event == "DISCONNECT":
        if not app._exiting:
            app._exiting = True
            app.exit()
    elif event.event == "AUDIO_ERROR":
        msg = f"Audio error: {event.reason}, visualization continues silently"
        app.post_message(LogMessage(msg, level="warning"))
    elif event.event == "KEY_PRESSED":
        await dispatch_key_event(
            event.key,
            app.renderer_dispatch_table,
            app,
        )


async def stderr_monitor_task(app: "PlatyplatyApp") -> None:
    """Monitor renderer stderr for events.

    Runs as a Textual worker. Uses CancelledError for shutdown.

    Args:
        app: The Textual application instance.
    """
    process = app._renderer_process
    if process is None or process.stderr is None:
        return

    try:
        async for payload in read_netstrings_from_stderr(process.stderr):
            await process_stderr_line(payload, app)
    except asyncio.CancelledError:
        pass  # Normal shutdown via Textual worker cancellation

    # Renderer process exited - trigger shutdown
    if not app._exiting:
        app._exiting = True
        app.exit()

