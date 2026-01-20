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
    return await save_to_path(args, ctx, base_dir)


async def save_to_associated(ctx: "AppContext") -> tuple[bool, str | None]:
    """Save to the associated filename if it exists."""
    if ctx.playlist.associated_filename is None:
        return (False, "Error: No file name")
    return perform_save(ctx, ctx.playlist.associated_filename)


async def save_to_path(
    path_arg: str, ctx: "AppContext", base_dir: Path
) -> tuple[bool, str | None]:
    """Save to the specified path."""
    filepath = expand_command_path(path_arg, base_dir)
    if not filepath.suffix.lower() == ".platy":
        return (False, "Error: a playlist filename must end with .platy")
    return perform_save(ctx, filepath)


def perform_save(ctx: "AppContext", filepath: Path) -> tuple[bool, str | None]:
    """Perform the actual save operation."""
    try:
        ctx.playlist.save_to_file(filepath)
    except Exception as e:
        return (False, f"Error: could not save playlist: {e}")
    return (True, None)
