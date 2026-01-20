#!/usr/bin/env python3
"""Load playlist command handler.

Implements the :load command for loading .platy playlist files.
"""

from pathlib import Path
from typing import TYPE_CHECKING

from platyplaty.commands.load_helpers import load_and_play_playlist

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext


async def execute(
    args: str | None, ctx: "AppContext", app: "PlatyplatyApp", base_dir: Path
) -> tuple[bool, str | None]:
    """Execute the :load command.

    Args:
        args: Command arguments (path to playlist file).
        ctx: Application context.
        app: The Textual application.
        base_dir: Base directory for resolving relative paths.

    Returns:
        Tuple of (success, error_message). error_message is None on success.
    """
    if args is None:
        return (False, "Error: load requires a path argument")
    return await load_and_play_playlist(args, ctx, app, base_dir)
