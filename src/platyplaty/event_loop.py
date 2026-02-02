#!/usr/bin/env python3
"""Stderr monitoring for Platyplaty.

Monitors renderer stderr for PLATYPLATY events (DISCONNECT, AUDIO_ERROR,
QUIT, KEY_PRESSED).
"""

import asyncio
from typing import TYPE_CHECKING

from textual.events import Key

from platyplaty.crash_handler import handle_renderer_crash
from platyplaty.messages import LogMessage
from platyplaty.netstring_reader import read_netstrings_from_stderr
from platyplaty.stderr_parser import parse_stderr_event
from platyplaty.types import StderrEvent
from platyplaty.dispatch_tables import normalize_key

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext

async def process_stderr_line(
    line: str,
    ctx: "AppContext",
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

    await _handle_stderr_event(event, ctx, app)


async def _handle_stderr_event(
    event: StderrEvent,
    ctx: "AppContext",
    app: "PlatyplatyApp",
) -> None:
    """Handle a parsed PLATYPLATY stderr event.

    Args:
        event: The parsed event.
        app: The Textual application instance.
    """
    if event.event == "QUIT" or event.event == "DISCONNECT":
        if not ctx.exiting:
            ctx.exiting = True
            app.exit()
    elif event.event == "AUDIO_ERROR":
        msg = f"Audio error: {event.reason}, visualization continues silently"
        app.post_message(LogMessage(msg, level="warning"))
    elif event.event == "KEY_PRESSED":
        key = normalize_key(event.key)
        char = key if len(key) == 1 else None
        app.post_message(Key(key=key, character=char))


async def stderr_monitor_task(ctx: "AppContext", app: "PlatyplatyApp") -> None:
    """Monitor renderer stderr for events.

    Runs as a Textual worker. Uses CancelledError for shutdown.

    Args:
        app: The Textual application instance.
    """
    process = ctx.renderer_process
    if process is None or process.stderr is None:
        return

    try:
        async for payload in read_netstrings_from_stderr(process.stderr):
            await process_stderr_line(payload, ctx, app)
    except asyncio.CancelledError:
        pass  # Normal shutdown via Textual worker cancellation

    # Ensure process fully terminated before handling crash
    assert ctx.renderer_process is not None
    await ctx.renderer_process.wait()

    # Deliberate exit (QUIT/DISCONNECT) - do nothing
    if ctx.exiting:
        return

    # Renderer crashed - check if preset was involved
    if ctx.preset_sent_to_renderer is not None:
        # Preset crash - handle recovery
        await handle_renderer_crash(ctx, app)
    else:
        # Non-preset crash - exit the application
        ctx.exiting = True
        app.exit(message="Renderer crashed unexpectedly", return_code=1)
