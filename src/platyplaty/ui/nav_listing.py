"""Listing operations for navigation state.

This module provides functions for managing directory listings
in the navigation state. These are package-private functions
used by the nav_state module family.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from platyplaty.ui.directory import list_directory
from platyplaty.ui.directory_types import DirectoryEntry, DirectoryListing
from platyplaty.ui.nav_types import find_index_by_name

if TYPE_CHECKING:
    from platyplaty.ui.nav_state import NavigationState


def refresh_listing(state: NavigationState) -> None:
    """Refresh the directory listing for the current directory.

    Args:
        state: The navigation state to update.
    """
    state._listing = list_directory(state.current_dir)


def get_selected_index(state: NavigationState) -> int | None:
    """Get the index of the currently selected item.

    Args:
        state: The navigation state to query.

    Returns:
        The index of the selected item, or None if no selection.
    """
    if not state._listing or not state._listing.entries:
        return None
    if state.selected_name is None:
        return None
    return find_index_by_name(state._listing, state.selected_name)


def is_empty_or_inaccessible(state: NavigationState) -> bool:
    """Check if current directory is empty or inaccessible.

    Args:
        state: The navigation state to query.

    Returns:
        True if the directory is empty or inaccessible.
    """
    if not state._listing:
        return True
    if state._listing.permission_denied:
        return True
    return len(state._listing.entries) == 0


def get_listing(state: NavigationState) -> DirectoryListing | None:
    """Get the current directory listing.

    Args:
        state: The navigation state to query.

    Returns:
        The DirectoryListing for the current directory.
    """
    return state._listing


def get_selected_entry(state: NavigationState) -> DirectoryEntry | None:
    """Get the currently selected entry.

    Args:
        state: The navigation state to query.

    Returns:
        The selected DirectoryEntry, or None if no selection.
    """
    index = get_selected_index(state)
    if index is None or not state._listing:
        return None
    return state._listing.entries[index]
