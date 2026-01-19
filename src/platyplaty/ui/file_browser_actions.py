"""Playlist-related action functions for the file browser.

This module provides functions for the "a" key (add preset or load playlist),
ENTER key (preview preset), and J/K keys (play next/previous .milk file).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from platyplaty.preset_validator import is_readable
from platyplaty.ui.directory_types import EntryType
from platyplaty.ui.file_browser_error import show_transient_error

if TYPE_CHECKING:
    from platyplaty.ui.file_browser import FileBrowser


async def action_add_preset_or_load_playlist(browser: FileBrowser) -> None:
    """Handle 'a' key: add preset to playlist or load .platy file.

    Behavior depends on the selected entry type:
    - .milk file or symlink to .milk: add to playlist
    - .platy file or symlink to .platy: load playlist
    - directory, symlink to directory, or broken symlink: show error

    Args:
        browser: The file browser instance.
    """
    entry = browser.get_selected_entry()
    if entry is None:
        return
    suffix = entry.path.suffix.lower()
    is_file_type = entry.entry_type in (EntryType.FILE, EntryType.SYMLINK_TO_FILE)
    if is_file_type and suffix == ".milk":
        _handle_add_milk_preset(browser, entry)
        return
    if is_file_type and suffix == ".platy":
        # TODO: Implement in TASK-22500
        return
    show_transient_error(browser, "Cannot add: not a playlist or preset")


def _handle_add_milk_preset(browser: FileBrowser, entry) -> None:
    """Add a .milk preset to the playlist.

    Checks readability and adds to playlist if readable.
    Shows error if not readable.

    Args:
        browser: The file browser instance.
        entry: The directory entry to add.
    """
    path = entry.path
    if not is_readable(path):
        show_transient_error(browser, "Cannot add: file not readable")
        return
    ctx = browser.app.ctx
    ctx.playlist.add_preset(path)
