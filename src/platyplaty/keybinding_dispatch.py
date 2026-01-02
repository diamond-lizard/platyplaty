#!/usr/bin/env python3
"""Keybinding dispatch for Platyplaty.

Routes key events from terminal and renderer to their configured actions.
Terminal events use keybindings.client, renderer events use keybindings.renderer.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.event_loop import EventLoopState

# Type alias for action callbacks (TASK-3400)
# Actions receive the shared state and perform their operation synchronously.
# Async operations (like sending commands) are handled via state flags that
# the main loop monitors.
ActionCallback = Callable[["EventLoopState"], None]

# Type alias for dispatch tables mapping key names to callbacks
DispatchTable = dict[str, ActionCallback]


def action_quit(state: "EventLoopState") -> None:
    """Set shutdown flag to trigger graceful exit.

    Args:
        state: Shared event loop state.
    """
    state.shutdown_requested = True
    state.shutdown_event.set()


def action_next_preset(state: "EventLoopState") -> None:
    """Advance to the next preset in the playlist.

    Silently ignores if renderer not ready or if at end with loop disabled.

    Args:
        state: Shared event loop state.
    """
    if not state.renderer_ready:
        return
    next_path = state.playlist.next()
    if next_path is not None:
        state.command_queue.put_nowait(("LOAD PRESET", {"path": str(next_path)}))


def action_previous_preset(state: "EventLoopState") -> None:
    """Go back to the previous preset in the playlist.

    Silently ignores if renderer not ready or if at start with loop disabled.

    Args:
        state: Shared event loop state.
    """
    if not state.renderer_ready:
        return
    prev_path = state.playlist.previous()
    if prev_path is not None:
        state.command_queue.put_nowait(("LOAD PRESET", {"path": str(prev_path)}))


def build_renderer_dispatch_table(
    next_preset_key: str,
    previous_preset_key: str,
    quit_key: str,
) -> DispatchTable:
    """Build dispatch table for renderer window key events.

    Args:
        next_preset_key: Key bound to next preset action.
        previous_preset_key: Key bound to previous preset action.
        quit_key: Key bound to quit action.

    Returns:
        Dispatch table mapping keys to action callbacks.
    """
    return {
        next_preset_key: action_next_preset,
        previous_preset_key: action_previous_preset,
        quit_key: action_quit,
    }


def build_client_dispatch_table(quit_key: str | None) -> DispatchTable:
    """Build dispatch table for terminal key events.

    Args:
        quit_key: Key bound to quit action, or None if not bound.

    Returns:
        Dispatch table mapping keys to action callbacks.
    """
    table: DispatchTable = {}
    if quit_key is not None:
        table[quit_key] = action_quit
    return table


def dispatch_key_event(
    key: str,
    table: DispatchTable,
    state: "EventLoopState",
) -> bool:
    """Dispatch a key event using the given dispatch table.

    Looks up the key in the table and invokes the callback if found.
    Unbound keys are silently ignored (TASK-3800).

    Args:
        key: The key name from the event.
        table: Dispatch table mapping keys to callbacks.
        state: Shared event loop state.

    Returns:
        True if key was bound and callback invoked, False otherwise.
    """
    callback = table.get(key)
    if callback is None:
        return False
    callback(state)
    return True
