"""Memory operations for navigation state.

This module provides functions for managing directory memory
(selection and scroll position persistence) in the navigation state.
These are package-private functions used by the nav_state module family.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from platyplaty.ui.nav_types import DirectoryMemory, find_name_in_listing

if TYPE_CHECKING:
    from platyplaty.ui.nav_state import NavigationState


def set_initial_selection(state: NavigationState) -> None:
    """Set selection to first item or None if empty.

    Args:
        state: The navigation state to update.
    """
    if not state._listing or not state._listing.entries:
        state.selected_name = None
        return
    state.selected_name = state._listing.entries[0].name


def save_current_memory(state: NavigationState) -> None:
    """Save current selection and scroll position to directory memory.

    Args:
        state: The navigation state to save.
    """
    key = str(state.current_dir)
    state._directory_memory[key] = DirectoryMemory(
        selected_name=state.selected_name,
        scroll_offset=state.scroll_offset,
    )


def try_restore_remembered_name(
    state: NavigationState,
    memory: DirectoryMemory,
) -> bool:
    """Try to restore a remembered selection.

    Args:
        state: The navigation state to update.
        memory: The directory memory to restore from.

    Returns:
        True if the remembered name was found and restored.
    """
    if not memory.selected_name:
        return False
    if not state._listing or not state._listing.entries:
        return False
    if not find_name_in_listing(state._listing, memory.selected_name):
        return False
    state.selected_name = memory.selected_name
    state.scroll_offset = memory.scroll_offset
    return True


def restore_memory(state: NavigationState) -> None:
    """Restore selection and scroll position from directory memory.

    Args:
        state: The navigation state to update.
    """
    key = str(state.current_dir)
    memory = state._directory_memory.get(key)
    if memory and try_restore_remembered_name(state, memory):
        return
    set_initial_selection(state)
    state.scroll_offset = 0


def restore_scroll_from_memory(state: NavigationState) -> None:
    """Restore scroll offset from directory memory if available.

    Args:
        state: The navigation state to update.
    """
    key = str(state.current_dir)
    memory = state._directory_memory.get(key)
    if memory:
        state.scroll_offset = memory.scroll_offset
        return
    state.scroll_offset = 0
