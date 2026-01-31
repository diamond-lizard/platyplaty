#!/usr/bin/env python3
"""Navigation utilities for the cd command.

Provides functions for checking same-directory conditions and
performing directory navigation in the file browser.
"""

import os
from pathlib import Path
from typing import TYPE_CHECKING

from platyplaty.ui.indicator_cache import refresh_indicator_cache
from platyplaty.ui.nav_listing import get_selected_entry, refresh_listing
from platyplaty.ui.nav_memory import restore_memory, save_current_memory

if TYPE_CHECKING:
    from platyplaty.ui.file_browser import FileBrowser


def is_same_directory(current: Path, target: Path) -> bool:
    """Check if two paths refer to the same logical directory.

    Compares paths after normalization (removing '.', '..', and trailing
    slashes) but WITHOUT resolving symlinks. This means a symlink and
    its target are considered different directories.

    Args:
        current: The current directory path.
        target: The target directory path to compare.

    Returns:
        True if both paths normalize to the same logical path.
    """
    normalized_current = os.path.normpath(str(current))
    normalized_target = os.path.normpath(str(target))
    return normalized_current == normalized_target


def navigate_to_directory(browser: "FileBrowser", target: Path) -> bool:
    """Navigate the file browser to a target directory.

    Saves current selection to memory, updates the current directory,
    refreshes the listing, restores memory for the new directory,
    and updates the display.

    Args:
        browser: The FileBrowser widget to navigate.
        target: The directory path to navigate to.

    Returns:
        True if navigation occurred, False if it was a no-op.
    """
    if is_same_directory(browser.current_dir, target):
        return False
    save_current_memory(browser._nav_state)
    browser._nav_state.current_dir = target
    browser.current_dir = target
    refresh_listing(browser._nav_state)
    restore_memory(browser._nav_state)
    entry = get_selected_entry(browser._nav_state)
    if entry is not None:
        refresh_indicator_cache(entry.entry_type, entry.path)
    browser.refresh_panes()
    return True
