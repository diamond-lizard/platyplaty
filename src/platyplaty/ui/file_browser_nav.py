"""Navigation action functions for the file browser widget.

This module provides functions for handling left/right navigation
actions in the file browser. These are package-private functions
used by the FileBrowser class.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from platyplaty.errors import InaccessibleDirectoryError
from platyplaty.ui.file_browser_error import (
    open_in_editor_action,
    show_transient_error,
)
from platyplaty.ui.file_browser_sync import refresh_panes

if TYPE_CHECKING:
    from platyplaty.ui.file_browser import FileBrowser


async def action_nav_left(browser: FileBrowser) -> None:
    """Navigate to parent directory.

    No-op if at filesystem root. Shows error if parent inaccessible.

    Args:
        browser: The file browser instance.
    """
    try:
        moved = browser._nav_state.move_left()
    except InaccessibleDirectoryError:
        show_transient_error(browser, "permission denied")
        return
    if not moved:
        return
    refresh_panes(browser)


async def action_nav_right(browser: FileBrowser) -> None:
    """Navigate into directory or open file in editor.

    For directories: navigates into them.
    For files: opens in external editor.
    For broken symlinks: no-op.
    Shows error if directory inaccessible or no editor found.

    Args:
        browser: The file browser instance.
    """
    file_path = handle_nav_right(browser)
    if file_path is None:
        return
    await open_in_editor_action(browser, file_path)


def handle_nav_right(browser: FileBrowser) -> str | None:
    """Handle right navigation, returning file path if editor needed.

    Args:
        browser: The file browser instance.

    Returns:
        File path string if a file should be opened, None otherwise.
    """
    try:
        file_path = browser._nav_state.move_right()
    except InaccessibleDirectoryError:
        show_transient_error(browser, "permission denied")
        return None
    if file_path is not None:
        return file_path
    refresh_panes(browser)
    return None
