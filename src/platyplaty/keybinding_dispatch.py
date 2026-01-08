#!/usr/bin/env python3
"""Keybinding dispatch for Platyplaty.

Routes key events from terminal and renderer to their configured actions.
Terminal events use keybindings.client, renderer events use keybindings.renderer.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext


from platyplaty.dispatch_tables import DispatchTable


async def dispatch_key_event(
    key: str,
    table: DispatchTable,
    ctx: "AppContext",
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
        if not ctx.exiting:
            ctx.exiting = True
            app.exit()
    return True
