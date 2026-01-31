#!/usr/bin/env python3
"""Change directory command handler.

Implements the :cd command for navigating the file browser to a new directory.
"""

from pathlib import Path
from typing import TYPE_CHECKING

from platyplaty.commands.cd_navigate import navigate_to_directory
from platyplaty.commands.cd_path_expand import expand_cd_path
from platyplaty.commands.cd_validation import validate_cd_path

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext


async def execute(
    args: str | None, ctx: "AppContext", app: "PlatyplatyApp", base_dir: Path
) -> tuple[bool, str | None]:
    """Execute the :cd command.

    Navigates the file browser to the specified directory. Supports absolute
    paths, relative paths, tilde expansion, and environment variable expansion.

    Args:
        args: Command arguments (path to navigate to, or None for home).
        ctx: Application context.
        app: The Textual application.
        base_dir: Base directory for resolving relative paths.

    Returns:
        Tuple of (success, error_message). error_message is None on success.
    """
    if args is None:
        args = ""
    expanded_path, error = expand_cd_path(args, base_dir)
    if error is not None:
        return (False, error)
    assert expanded_path is not None
    validation_error = validate_cd_path(expanded_path)
    if validation_error is not None:
        return (False, validation_error)
    from platyplaty.ui.file_browser import FileBrowser

    browser = app.query_one("#file_browser", FileBrowser)
    navigate_to_directory(browser, expanded_path)
    return (True, None)
