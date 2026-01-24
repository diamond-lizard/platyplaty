#!/usr/bin/env python3
"""Command prompt activation for Platyplaty.

Provides the function to show the command prompt from keybinding dispatch.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext


async def show_command_prompt(ctx: "AppContext", app: "PlatyplatyApp") -> None:
    """Show the command prompt and set up the callback.

    Args:
        ctx: Application context.
        app: The Textual application.
    """
    from platyplaty.command_prompt_handler import create_command_callback
    from platyplaty.ui.command_line import CommandLine

    command_line = app.query_one(CommandLine)
    callback = create_command_callback(ctx, app)
    previous_focus_id = get_previous_focus_id(ctx)
    command_line.show_command_prompt(callback, previous_focus_id)


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
