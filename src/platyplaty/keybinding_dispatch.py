#!/usr/bin/env python3
"""Keybinding dispatch for Platyplaty.

Routes key events from terminal and renderer to their configured actions.
Terminal events use keybindings.client, renderer events use keybindings.renderer.
"""

from platyplaty.event_loop import EventLoopState
from platyplaty.types import KeyPressedEvent


def dispatch_client_key(event: KeyPressedEvent, state: EventLoopState) -> None:
    """Dispatch a terminal key event to client keybindings.

    Args:
        event: The key event from terminal input.
        state: Shared event loop state.
    """
    quit_key = state.client_keybindings.quit
    if quit_key is not None and event.key == quit_key:
        state.shutdown_requested = True
