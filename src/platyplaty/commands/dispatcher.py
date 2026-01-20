#!/usr/bin/env python3
"""Command dispatcher for the command prompt.

Dispatches commands to their respective handler modules.
"""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext


async def execute_command(
    name: str,
    args: str | None,
    ctx: "AppContext",
    app: "PlatyplatyApp",
    base_dir: Path,
) -> tuple[bool, str | None]:
    """Execute a command by name.

    Args:
        name: The command name (e.g., "load", "save").
        args: Command arguments, or None.
        ctx: Application context.
        app: The Textual application.
        base_dir: Base directory for resolving relative paths.

    Returns:
        Tuple of (success, error_message). error_message is None on success.
    """
    if name == "load":
        from platyplaty.commands.load_playlist import execute
        return await execute(args, ctx, app, base_dir)
    return (False, f"Command not found: '{name}'")


def get_file_browser_current_dir(app: "PlatyplatyApp") -> Path:
    """Get the current directory from the file browser widget.

    This is the directory shown in the middle pane of the file browser,
    used for resolving relative paths in commands like :load.

    Args:
        app: The Textual application.

    Returns:
        The current directory path from the file browser.
    """
    from platyplaty.ui.file_browser import FileBrowser
    file_browser = app.query_one("#file_browser", FileBrowser)
    return file_browser.current_dir
