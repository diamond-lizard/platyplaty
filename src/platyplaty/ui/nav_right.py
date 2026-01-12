"""Right navigation for navigation state.

This module provides the move_right function for navigating into
directories or returning file paths for editing. This is a
package-private function used by the nav_state module family.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from platyplaty.ui.directory_types import DirectoryEntry, EntryType
from platyplaty.ui.nav_access import check_directory_accessible
from platyplaty.ui.indicator_cache import refresh_indicator_cache
from platyplaty.ui.nav_listing import (
    get_selected_entry,
    is_empty_or_inaccessible,
    refresh_listing,
)
from platyplaty.ui.nav_memory import restore_memory, save_current_memory

if TYPE_CHECKING:
    from platyplaty.ui.nav_state import NavigationState


def move_right(state: NavigationState) -> str | None:
    """Navigate into selected directory or return file path for editor.

    For directories and symlinks to directories: navigates into them.
    For files and symlinks to files: returns the path for editor.
    For broken symlinks: no-op.
    No-op if directory is empty or inaccessible.

    Args:
        state: The navigation state to update.

    Returns:
        Path string if a file should be opened in editor, None otherwise.

    Raises:
        InaccessibleDirectoryError: If target directory cannot be accessed.
    """
    if is_empty_or_inaccessible(state):
        return None
    entry = get_selected_entry(state)
    if entry is None:
        return None
    return _handle_move_right_entry(state, entry)


def _handle_move_right_entry(
    state: NavigationState,
    entry: DirectoryEntry,
) -> str | None:
    """Handle move_right for a specific entry type.

    Args:
        state: The navigation state to update.
        entry: The selected directory entry.

    Returns:
        Path string if a file should be opened in editor, None otherwise.
    """
    if entry.entry_type == EntryType.BROKEN_SYMLINK:
        return None
    if entry.entry_type in (EntryType.FILE, EntryType.SYMLINK_TO_FILE):
        return str(state.current_dir / entry.name)
    if entry.entry_type in (EntryType.DIRECTORY, EntryType.SYMLINK_TO_DIRECTORY):
        _navigate_into_directory(state, entry.name)
    return None


def _navigate_into_directory(state: NavigationState, name: str) -> None:
    """Navigate into a subdirectory.

    Args:
        state: The navigation state to update.
        name: The name of the directory to enter.

    Raises:
        InaccessibleDirectoryError: If target directory cannot be accessed.
    """
    target = state.current_dir / name
    check_directory_accessible(target)
    save_current_memory(state)
    state.current_dir = state.current_dir / name
    refresh_listing(state)
    restore_memory(state)
    entry = get_selected_entry(state)
    if entry is not None:
        refresh_indicator_cache(entry.entry_type, entry.path)
