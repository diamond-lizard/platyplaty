#!/usr/bin/env python3
"""Keybinding dispatch for Platyplaty.

Routes key events from terminal and renderer to their configured actions.
Terminal events use keybindings.client, renderer events use keybindings.renderer.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp


# Type alias for dispatch tables mapping key names to action names
DispatchTable = dict[str, str]


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
        Dispatch table mapping keys to action names.
    """
    return {
        next_preset_key: "next_preset",
        previous_preset_key: "previous_preset",
        quit_key: "quit",
    }


def build_client_dispatch_table(quit_key: str | None) -> DispatchTable:
    """Build dispatch table for terminal key events.

    Args:
        quit_key: Key bound to quit action, or None if not bound.

    Returns:
        Dispatch table mapping keys to action names.
    """
    table: DispatchTable = {}
    if quit_key is not None:
        table[quit_key] = "quit"
    return table



async def dispatch_key_event(
    key: str,
    table: DispatchTable,
    app: "PlatyplatyApp",
) -> bool:
    """Dispatch a key event using the given dispatch table.

    Looks up the key in the table and invokes the action via run_action.
    Unbound keys are silently ignored (TASK-3800).

    Args:
        key: The key name from the event.
        table: Dispatch table mapping keys to action names.
        app: The Textual application instance.

    Returns:
        True if key was bound and action invoked, False otherwise.
    """
    action_name = table.get(key)
    if action_name is None:
        return False
    try:
        await app.run_action(action_name)
    except ConnectionError:
        if not app._exiting:
            app._exiting = True
            app.exit()
    return True
