"""Basic move operations for navigation state.

This module provides functions for moving the selection up and down
in the file browser. These are package-private functions used by
the nav_state module family.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from platyplaty.ui.nav_listing import get_selected_index, is_empty_or_inaccessible

if TYPE_CHECKING:
    from platyplaty.ui.nav_state import NavigationState


def move_up(state: NavigationState) -> bool:
    """Move selection up by one item.

    No-op if directory is empty or inaccessible, or already at top.

    Args:
        state: The navigation state to update.

    Returns:
        True if selection moved, False otherwise.
    """
    if is_empty_or_inaccessible(state):
        return False
    assert state._listing is not None
    index = get_selected_index(state)
    if index is None or index <= 0:
        return False
    state.selected_name = state._listing.entries[index - 1].name
    return True


def move_down(state: NavigationState) -> bool:
    """Move selection down by one item.

    No-op if directory is empty or inaccessible, or already at bottom.

    Args:
        state: The navigation state to update.

    Returns:
        True if selection moved, False otherwise.
    """
    if is_empty_or_inaccessible(state):
        return False
    assert state._listing is not None
    index = get_selected_index(state)
    if index is None:
        return False
    max_index = len(state._listing.entries) - 1
    if index >= max_index:
        return False
    state.selected_name = state._listing.entries[index + 1].name
    return True
