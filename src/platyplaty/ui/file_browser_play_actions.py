"""Play previous/next preset actions for the file browser.

This module provides J/K key actions to skip to the previous/next .milk
file in the directory and play it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from platyplaty.ui.directory_types import DirectoryEntry, EntryType

if TYPE_CHECKING:
    from platyplaty.ui.file_browser import FileBrowser


async def action_play_previous_preset(browser: FileBrowser) -> None:
    """Play the previous .milk file in the directory.

    Skips over directories, symlinks to directories, .platy files,
    and broken symlinks. If no previous .milk file exists, this is a no-op.

    Args:
        browser: The file browser instance.
    """
    await _play_adjacent_preset(browser, direction=-1)


async def action_play_next_preset(browser: FileBrowser) -> None:
    """Play the next .milk file in the directory.

    Skips over directories, symlinks to directories, .platy files,
    and broken symlinks. If no next .milk file exists, this is a no-op.

    Args:
        browser: The file browser instance.
    """
    await _play_adjacent_preset(browser, direction=1)


async def _play_adjacent_preset(browser: FileBrowser, direction: int) -> None:
    """Find and play an adjacent .milk preset.

    Args:
        browser: The file browser instance.
        direction: -1 for previous, 1 for next.
    """
    from platyplaty.ui.file_browser_preset_preview import _preview_milk_preset

    target_index = _find_adjacent_milk_index(browser, direction)
    if target_index is None:
        return
    browser.selected_index = target_index
    browser._nav_state.adjust_scroll(browser.size.height - 1)
    browser._middle_scroll_offset = browser._nav_state.scroll_offset
    browser.refresh()
    entry = browser.get_selected_entry()
    if entry is not None:
        await _preview_milk_preset(browser, entry.path)


def _find_adjacent_milk_index(browser: FileBrowser, direction: int) -> int | None:
    """Find the index of the next/previous .milk file.

    Args:
        browser: The file browser instance.
        direction: -1 for previous, 1 for next.

    Returns:
        Index of the adjacent .milk file, or None if not found.
    """
    listing = browser._middle_listing
    if listing is None or not listing.entries:
        return None
    current = browser.selected_index
    if current is None:
        return None
    index = current + direction
    while 0 <= index < len(listing.entries):
        entry = listing.entries[index]
        if _is_playable_milk(entry):
            return index
        index += direction
    return None


def _is_playable_milk(entry: DirectoryEntry) -> bool:
    """Check if an entry is a playable .milk file.

    Args:
        entry: The directory entry to check.

    Returns:
        True if entry is a .milk file or symlink to .milk file.
    """
    suffix = entry.path.suffix.lower()
    is_file = entry.entry_type in (EntryType.FILE, EntryType.SYMLINK_TO_FILE)
    return suffix == ".milk" and is_file
