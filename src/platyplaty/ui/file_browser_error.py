"""Error display and editor functions for the file browser widget.

This module provides functions for showing transient errors and
opening files in the external editor. These are package-private
functions used by the FileBrowser class and navigation modules.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from platyplaty.errors import NoEditorFoundError
from platyplaty.ui.command_line import CommandLine
from platyplaty.ui.editor import open_in_editor
from platyplaty.ui.file_browser_refresh import refresh_listings
from platyplaty.ui.file_browser_sync import sync_from_nav_state

if TYPE_CHECKING:
    from platyplaty.ui.file_browser import FileBrowser


def show_transient_error(browser: FileBrowser, message: str) -> None:
    """Show a transient error message at the bottom of the screen.

    Displays black text on red background for 0.5 seconds.

    Args:
        browser: The file browser instance.
        message: The error message to display.
    """
    cmd_line = browser.app.query_one("#command_line", CommandLine)
    cmd_line.show_transient_error(message)


async def open_in_editor_action(browser: FileBrowser, file_path: str) -> None:
    """Open a file in the external editor.

    Suspends the app, runs the editor, then refreshes after exit.

    Args:
        browser: The file browser instance.
        file_path: Path to the file to edit.
    """
    try:
        await open_in_editor(browser.app, file_path)
    except NoEditorFoundError:
        show_transient_error(browser, "No editor found")
        return
    browser._nav_state.refresh_after_editor()
    sync_from_nav_state(browser)
    refresh_listings(browser)
    browser.refresh()
