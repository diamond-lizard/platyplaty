#!/usr/bin/env python3
"""Save playlist command handler.

Implements the :save command for saving .platy playlist files.
"""

from pathlib import Path
from typing import TYPE_CHECKING

from platyplaty.commands.load_helpers import expand_command_path

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext


async def execute(
    args: str | None, ctx: "AppContext", app: "PlatyplatyApp", base_dir: Path
) -> tuple[bool, str | None]:
    """Execute the :save command.

    Args:
        args: Optional path argument. If None, saves to associated filename.
        ctx: Application context.
        app: The Textual application.
        base_dir: Base directory for resolving relative paths.

    Returns:
        Tuple of (success, error_message). error_message is None on success.
    """
    if args is None:
        return await save_to_associated(ctx)
    return await save_to_path(args, ctx, app, base_dir)


async def save_to_associated(ctx: "AppContext") -> tuple[bool, str | None]:
    """Save to the associated filename if it exists."""
    if ctx.playlist.associated_filename is None:
        return (False, "Error: No file name")
    return perform_save(ctx, ctx.playlist.associated_filename)


async def save_to_path(
    path_arg: str, ctx: "AppContext", app: "PlatyplatyApp", base_dir: Path
) -> tuple[bool, str | None]:
    """Save to the specified path."""
    filepath = expand_command_path(path_arg, base_dir)
    if filepath.suffix.lower() != ".platy":
        return (False, "Error: a playlist filename must end with .platy")
    return await check_and_save(filepath, ctx, app)


async def check_and_save(
    filepath: Path, ctx: "AppContext", app: "PlatyplatyApp"
) -> tuple[bool, str | None]:
    """Check if file exists and show overwrite prompt if needed."""
    if filepath.exists():
        await show_overwrite_prompt(filepath, ctx, app)
        return (True, None)
    return perform_save(ctx, filepath)


async def show_overwrite_prompt(
    filepath: Path, ctx: "AppContext", app: "PlatyplatyApp"
) -> None:
    """Show confirmation prompt for overwriting existing file."""
    from platyplaty.ui.command_line import CommandLine
    from platyplaty.focus_helpers import get_previous_focus_id

    command_line = app.query_one("#command_line", CommandLine)
    msg = "File exists. Overwrite? (y/n)"

    async def on_response(confirmed: bool) -> None:
        if confirmed:
            perform_save(ctx, filepath)

    previous_focus_id = get_previous_focus_id(ctx)
    command_line.show_confirmation_prompt(msg, on_response, previous_focus_id)

def perform_save(ctx: "AppContext", filepath: Path) -> tuple[bool, str | None]:
    """Perform the actual save operation."""
    try:
        ctx.playlist.save_to_file(filepath)
    except Exception as e:
        return (False, f"Error: could not save playlist: {e}")
    return (True, None)
