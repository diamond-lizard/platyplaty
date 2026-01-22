"""Initialization function for the file browser widget.

This module provides the init_browser function that sets up the
FileBrowser widget's state. This is a package-private module.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from platyplaty.dispatch_tables import DispatchTable
from platyplaty.errors import InaccessibleDirectoryError
from platyplaty.ui.file_browser_refresh import refresh_listings
from platyplaty.ui.layout_state import LayoutState
from platyplaty.ui.nav_state import NavigationState

if TYPE_CHECKING:
    from platyplaty.ui.file_browser import FileBrowser


def init_browser(
    browser: FileBrowser,
    dispatch_table: DispatchTable,
    starting_dir: Path | None,
) -> None:
    """Initialize the FileBrowser widget's state.

    Sets up the dispatch table, current directory, directory listings,
    and navigation state. Raises InaccessibleDirectoryError if the
    starting directory cannot be accessed.

    Args:
        browser: The FileBrowser instance to initialize.
        dispatch_table: Dispatch table for navigation key bindings.
        starting_dir: Initial directory to display. Defaults to CWD.
    """
    browser._dispatch_table = dispatch_table
    if starting_dir is None:
        # Use PWD to preserve the logical path through symlinks.
        # Path.cwd() uses getcwd(3) which returns the resolved physical path,
        # losing symlink information. PWD is maintained by the shell and
        # contains the logical path the user navigated.
        pwd = os.environ.get('PWD')
        if pwd:
            browser.current_dir = Path(pwd)
        else:
            browser.current_dir = Path.cwd()
    else:
        # Use absolute() instead of resolve() to preserve symlinks in the path
        browser.current_dir = starting_dir.absolute()

    # Check if directory is accessible
    if not browser.current_dir.is_dir():
        raise InaccessibleDirectoryError(str(browser.current_dir))
    try:
        list(browser.current_dir.iterdir())
    except PermissionError:
        raise InaccessibleDirectoryError(str(browser.current_dir)) from None

    browser._middle_scroll_offset = 0
    browser._left_scroll_offset = 0
    browser._right_scroll_offset = 0

    # Cache for directory listings
    browser._left_listing = None
    browser._middle_listing = None
    browser._right_content = None
    browser._right_selected_index = None
    browser._layout_state = LayoutState.STANDARD
    browser._focused = True

    # Navigation state manager
    browser._nav_state = NavigationState(browser.current_dir)

    # Refresh listings on init
    refresh_listings(browser)
