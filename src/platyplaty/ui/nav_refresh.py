"""Refresh operations for navigation state.

This module provides functions for refreshing directory listings
after editor exits. This is a package-private function used by
the nav_state module family.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from platyplaty.ui.nav_listing import get_selected_index, refresh_listing
from platyplaty.ui.nav_types import find_name_in_listing

if TYPE_CHECKING:
    from platyplaty.ui.nav_state import NavigationState


def refresh_after_editor(state: NavigationState) -> None:
    """Refresh directory after editor exits and restore selection.

    Re-reads the current directory listing. If the previously selected
    filename still exists, keeps it selected. Otherwise, selects the
    item that is now at the previous index position (or the last item
    if the previous position is beyond the new list length).

    Args:
        state: The navigation state to update.
    """
    old_name = state.selected_name
    old_index = get_selected_index(state)
    refresh_listing(state)
    if _try_keep_selection(state, old_name):
        return
    _select_fallback(state, old_index)


def _try_keep_selection(state: NavigationState, old_name: str | None) -> bool:
    """Try to keep the same filename selected after refresh.

    Args:
        state: The navigation state to check.
        old_name: The name that was previously selected.

    Returns:
        True if the old name still exists in the listing.
    """
    if not old_name or not state._listing or not state._listing.entries:
        return False
    return find_name_in_listing(state._listing, old_name)


def _select_fallback(state: NavigationState, old_index: int | None) -> None:
    """Select fallback item when previous selection is gone.

    Args:
        state: The navigation state to update.
        old_index: The index of the previously selected item.
    """
    if not state._listing or not state._listing.entries:
        state.selected_name = None
        return
    max_index = len(state._listing.entries) - 1
    if old_index is not None and old_index <= max_index:
        state.selected_name = state._listing.entries[old_index].name
    else:
        state.selected_name = state._listing.entries[max_index].name
