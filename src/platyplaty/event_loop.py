#!/usr/bin/env python3
"""Event loop state and stderr monitoring for Platyplaty.

Provides shared state for event loop tasks and monitors renderer stderr
for PLATYPLATY events (DISCONNECT, AUDIO_ERROR, QUIT, KEY_PRESSED).
"""

import asyncio
from collections import deque
from typing import TYPE_CHECKING

from platyplaty.keybinding_dispatch import DispatchTable, dispatch_key_event
from platyplaty.netstring import read_netstrings_from_stderr
from platyplaty.stderr_parser import parse_stderr_event
from platyplaty.messages import LogMessage
from platyplaty.types import (
    ClientKeybindings,
    KeyPressedEvent,
    StderrEvent,
)

if TYPE_CHECKING:
    from platyplaty.playlist import Playlist
    from platyplaty.socket_client import SocketClient
    from platyplaty.app import PlatyplatyApp

# Maximum number of key events to queue during pending commands (REQ-0500)
MAX_KEY_EVENT_QUEUE = 8

class EventLoopState:
    """Shared state for the event loop tasks.

    Attributes:
        shutdown_requested: Set to True to request graceful shutdown.
        quit_received: Set to True when QUIT event received (no reconnect).
        disconnect_event: Set when DISCONNECT event received (reconnect).
        shutdown_event: Set when shutdown should occur.
        key_event_queue: Queue of key events waiting for command completion.
        command_pending: True while awaiting a socket command response.
        renderer_ready: True after renderer INIT succeeds.
        client_keybindings: Client keybindings for terminal input.
        renderer_dispatch_table: Dispatch table for renderer key events.
        playlist: The preset playlist for navigation.
        client: Socket client for renderer commands.
        command_queue: Queue for commands to send to renderer.
    """

    shutdown_requested: bool
    quit_received: bool
    disconnect_event: asyncio.Event
    shutdown_event: asyncio.Event
    key_event_queue: deque[KeyPressedEvent]
    command_pending: bool
    renderer_ready: bool
    client_keybindings: ClientKeybindings
    renderer_dispatch_table: DispatchTable
    playlist: "Playlist"
    client: "SocketClient"

    def __init__(
        self,
        client_keybindings: ClientKeybindings,
        renderer_dispatch_table: DispatchTable,
        playlist: "Playlist",
        client: "SocketClient",
    ) -> None:
        """Initialize event loop state."""
        self.shutdown_requested = False
        self.quit_received = False
        self.disconnect_event = asyncio.Event()
        self.shutdown_event = asyncio.Event()
        self.key_event_queue: deque[KeyPressedEvent] = deque(maxlen=MAX_KEY_EVENT_QUEUE)
        self.command_pending = False
        self.renderer_ready = False
        self.client_keybindings = client_keybindings
        self.renderer_dispatch_table = renderer_dispatch_table
        self.playlist = playlist
        self.client = client
        self.command_queue: asyncio.Queue[tuple[str, dict[str, str]]] = asyncio.Queue()


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
    if event.event == "QUIT":
        if not app._exiting:
            app._exiting = True
            app.exit()
    elif event.event == "DISCONNECT":
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



def process_queued_key_events(state: EventLoopState) -> list[KeyPressedEvent]:
    """Process queued key events after command response (TASK-2700).

    Drains the key event queue and returns events for dispatch.
    Called after a command response is received when command_pending
    transitions to False. Per REQ-0600, events are processed FIFO.

    Args:
        state: Shared event loop state.

    Returns:
        List of queued events in FIFO order for dispatch.
    """
    events = list(state.key_event_queue)
    state.key_event_queue.clear()
    return events


def clear_key_event_queue(state: EventLoopState) -> None:
    """Clear queued key events on shutdown or disconnect (REQ-0700).

    Args:
        state: Shared event loop state.
    """
    state.key_event_queue.clear()
