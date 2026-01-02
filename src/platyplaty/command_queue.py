#!/usr/bin/env python3
"""Command queue consumer for bridging sync callbacks to async commands.

This module provides an async task that consumes commands from the EventLoopState
command_queue and sends them to the renderer via SocketClient. Action callbacks
(which are synchronous) queue commands, and this consumer processes them.
"""

import asyncio
import logging
from typing import TYPE_CHECKING

from platyplaty.event_loop import process_queued_key_events
from platyplaty.keybinding_dispatch import dispatch_key_event
from platyplaty.socket_client import RendererError

if TYPE_CHECKING:
    from platyplaty.event_loop import EventLoopState

logger = logging.getLogger(__name__)


async def command_queue_consumer(state: "EventLoopState") -> None:
    """Consume commands from the queue and send to renderer.

    This task runs as a background asyncio task alongside stderr_task and
    auto_advance_loop. It pulls (command, params) tuples from state.command_queue
    and sends them via state.client.send_command().

    The task sets command_pending to True before sending and False after response.
    After each command completes, it processes any key events that queued during
    the command.

    Args:
        state: Shared event loop state containing command_queue and client.
    """
    while not state.shutdown_requested:
        try:
            command, params = await asyncio.wait_for(
                state.command_queue.get(),
                timeout=0.5,
            )
        except TimeoutError:
            continue

        state.command_pending = True
        try:
            await state.client.send_command(command, **params)
        except RendererError as e:
            logger.warning("Command %s failed: %s", command, e)
        finally:
            state.command_pending = False
            _dispatch_queued_events(state)


def _dispatch_queued_events(state: "EventLoopState") -> None:
    """Dispatch key events that queued during a pending command."""
    for event in process_queued_key_events(state):
        dispatch_key_event(event.key, state.renderer_dispatch_table, state)
