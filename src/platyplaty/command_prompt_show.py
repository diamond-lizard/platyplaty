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
    from platyplaty.focus_helpers import get_previous_focus_id
    from platyplaty.ui.command_line import CommandLine

    command_line = app.query_one(CommandLine)
    callback = create_command_callback(ctx, app)
    previous_focus_id = get_previous_focus_id(ctx)
    command_line.show_command_prompt(callback, previous_focus_id)

