#!/usr/bin/env python3
"""Quit handler for Platyplaty application.

Implements quit with confirmation prompts.
"""

from typing import TYPE_CHECKING

from platyplaty.ui.prompt_messages import PROMPT_QUIT, PROMPT_QUIT_UNSAVED

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext


async def handle_quit(ctx: "AppContext", app: "PlatyplatyApp") -> None:
    """Handle quit action with confirmation prompt.

    Shows different prompts based on unsaved changes state:
    - If unsaved changes: "There are unsaved changes. Quit anyway? (y/n)"
    - If no unsaved changes: "Quit? (y/n)"

    Args:
        ctx: Application context.
        app: The Textual application.
    """
    from platyplaty.ui.command_line import CommandLine
    from platyplaty.focus_helpers import get_previous_focus_id

    command_line = app.query_one("#command_line", CommandLine)
    message = PROMPT_QUIT_UNSAVED if ctx.playlist.dirty_flag else PROMPT_QUIT

    async def on_response(confirmed: bool) -> None:
        if confirmed:
            await app.graceful_shutdown()

    previous_focus_id = get_previous_focus_id(ctx)
    command_line.show_confirmation_prompt(message, on_response, previous_focus_id)
