#!/usr/bin/env python3
"""Confirmation prompts for the :load command.

Handles unsaved changes and non-empty playlist confirmation before loading.
"""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext


async def check_and_load(
    filepath: Path, ctx: "AppContext", app: "PlatyplatyApp"
) -> tuple[bool, str | None]:
    """Check for unsaved changes or non-empty playlist before loading.

    Shows confirmation prompts as needed:
    - If dirty_flag: show unsaved changes prompt (supersedes non-empty)
    - If non-empty: show clearing playlist prompt
    - If empty: load immediately

    Args:
        filepath: Path to the playlist file to load.
        ctx: Application context.
        app: The Textual application.

    Returns:
        Tuple of (success, error_message). Success means prompt shown or
        load started; actual load may happen later via callback.
    """
    if ctx.playlist.dirty_flag:
        await show_unsaved_changes_prompt(filepath, ctx, app)
        return (True, None)
    if len(ctx.playlist.presets) > 0:
        await show_non_empty_prompt(filepath, ctx, app)
        return (True, None)
    return await do_load(filepath, ctx, app)


async def show_unsaved_changes_prompt(
    filepath: Path, ctx: "AppContext", app: "PlatyplatyApp"
) -> None:
    """Show confirmation prompt for unsaved changes before loading."""
    from platyplaty.ui.command_line import CommandLine

    command_line = app.query_one("#command_line", CommandLine)
    msg = (
        "There are unsaved changes in the currently loaded playlist, "
        "replace anyway (y/n)?"
    )

    async def on_response(confirmed: bool) -> None:
        if confirmed:
            await do_load(filepath, ctx, app)

    command_line.show_confirmation_prompt(msg, on_response)


async def show_non_empty_prompt(
    filepath: Path, ctx: "AppContext", app: "PlatyplatyApp"
) -> None:
    """Show confirmation prompt for clearing non-empty playlist."""
    from platyplaty.ui.command_line import CommandLine

    command_line = app.query_one("#command_line", CommandLine)
    msg = "Load selected playlist, clearing current playlist? (y/n)"

    async def on_response(confirmed: bool) -> None:
        if confirmed:
            await do_load(filepath, ctx, app)

    command_line.show_confirmation_prompt(msg, on_response)


async def do_load(
    filepath: Path, ctx: "AppContext", app: "PlatyplatyApp"
) -> tuple[bool, str | None]:
    """Perform the actual load operation."""
    from platyplaty.commands.load_helpers import perform_load
    from platyplaty.playlist_snapshot import push_undo_snapshot

    push_undo_snapshot(ctx)
    return await perform_load(filepath, ctx, app)
