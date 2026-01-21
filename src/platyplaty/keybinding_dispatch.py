#!/usr/bin/env python3
"""Keybinding dispatch for Platyplaty.

Routes key events to their configured actions based on current focus.
Global keys work in all sections. Section-specific keys only work when
that section has focus and are silently ignored otherwise.
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


async def dispatch_focused_key_event(
    key: str,
    ctx: "AppContext",
    app: "PlatyplatyApp",
) -> bool:
    """Dispatch a key event based on current focus.

    First checks the global dispatch table, then checks the section-specific
    dispatch table based on ctx.current_focus. Section keys are silently
    ignored when the wrong section has focus.

    Args:
        key: The key name from the event.
        ctx: Application context containing focus state and dispatch tables.
        app: The Textual application instance.

    Returns:
        True if key was bound and action invoked, False otherwise.
    """
    # Handle ":" key for command prompt (not configurable, per TASK-15500)
    if key == "colon":
        await show_command_prompt(ctx, app)
        return True

    # Check global keys first
    if await dispatch_key_event(key, ctx.global_dispatch_table, ctx, app):
        return True

    # Check section-specific keys based on current focus
    if ctx.current_focus == "file_browser":
        return await dispatch_key_event(
            key, ctx.file_browser_dispatch_table, ctx, app
        )
    elif ctx.current_focus == "playlist":
        return await dispatch_key_event(
            key, ctx.playlist_dispatch_table, ctx, app
        )
    elif ctx.current_focus == "error_view":
        return await dispatch_key_event(
            key, ctx.error_view_dispatch_table, ctx, app
        )
    return False


async def show_command_prompt(ctx: "AppContext", app: "PlatyplatyApp") -> None:
    """Show the command prompt and set up the callback.

    Args:
        ctx: Application context.
        app: The Textual application.
    """
    from platyplaty.command_prompt_handler import create_command_callback
    from platyplaty.ui.command_prompt import CommandPrompt

    prompt = app.query_one(CommandPrompt)
    callback = create_command_callback(ctx, app)
    previous_focus_id = get_previous_focus_id(ctx)
    prompt.show_prompt(callback, previous_focus_id)


def get_previous_focus_id(ctx: "AppContext") -> str | None:
    """Get the widget ID for the previously focused section.

    Args:
        ctx: Application context with current_focus.

    Returns:
        Widget ID string for the focused section.
    """
    if ctx.current_focus == "file_browser":
        return "file_browser"
    if ctx.current_focus == "playlist":
        return "playlist"
    return None
