"""Up/down navigation functions for the file browser widget.

This module provides functions for moving selection up and down
in the file browser. These are package-private functions used by
the FileBrowser class.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from platyplaty.ui.file_browser_refresh import refresh_right_pane
from platyplaty.ui.file_browser_scroll import adjust_left_pane_scroll
from platyplaty.ui.file_browser_sync import sync_from_nav_state

if TYPE_CHECKING:
    from platyplaty.ui.file_browser import FileBrowser


async def action_nav_up(browser: FileBrowser) -> None:
    """Move selection up in the current directory.

    No-op if already at top, directory is empty, or inaccessible.

    Args:
        browser: The file browser instance.
    """
    if not browser._nav_state.move_up():
        return
    sync_from_nav_state(browser)
    adjust_left_pane_scroll(browser, browser.size.height - 1)
    refresh_right_pane(browser)
    browser.refresh()


async def action_nav_down(browser: FileBrowser) -> None:
    """Move selection down in the current directory.

    No-op if already at bottom, directory is empty, or inaccessible.

    Args:
        browser: The file browser instance.
    """
    if not browser._nav_state.move_down():
        return
    sync_from_nav_state(browser)
    adjust_left_pane_scroll(browser, browser.size.height - 1)
    refresh_right_pane(browser)
    browser.refresh()
