#!/usr/bin/env python3
"""Command prompt handler for wiring the command prompt to the dispatcher.

This module provides the callback function for CommandPrompt that parses
input and routes to the command dispatcher.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext


def parse_command_input(text: str) -> tuple[str, str | None]:
    """Parse command prompt input into command name and arguments.

    Commands and arguments are separated by a single space.
    Command names are case-sensitive and must be lowercase.

    Args:
        text: The input text from the command prompt.

    Returns:
        Tuple of (command_name, arguments). Arguments is None if not provided.
    """
    parts = text.split(" ", 1)
    name = parts[0]
    args = parts[1] if len(parts) > 1 else None
    return (name, args)


def create_command_callback(
    ctx: "AppContext", app: "PlatyplatyApp"
):
    """Create a callback for the CommandPrompt widget.

    The callback parses the input, executes the command, and handles
    the result (hiding prompt on success, showing error on failure).

    Args:
        ctx: Application context.
        app: The Textual application.

    Returns:
        An async callback function compatible with CommandPrompt.
    """
    async def callback(input_text: str) -> None:
        from platyplaty.commands.dispatcher import (
            execute_command,
            get_file_browser_current_dir,
        )
        from platyplaty.ui.command_prompt import CommandPrompt

        prompt = app.query_one(CommandPrompt)
        name, args = parse_command_input(input_text)
        base_dir = get_file_browser_current_dir(app)
        success, error = await execute_command(name, args, ctx, app, base_dir)
        if success:
            prompt.hide()
        else:
            show_command_error(app, error)

    return callback


def show_command_error(app: "PlatyplatyApp", error: str | None) -> None:
    """Show an error message via the transient error bar.

    Args:
        app: The Textual application.
        error: The error message to display.
    """
    from platyplaty.ui.transient_error import TransientErrorBar

    error_bar = app.query_one(TransientErrorBar)
    error_bar.show_error(error or "Unknown error")
