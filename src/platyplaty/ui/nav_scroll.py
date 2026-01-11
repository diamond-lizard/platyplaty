"""Scroll adjustment for navigation state.

This module provides functions for adjusting scroll position
to keep the selected item visible. This is a package-private
function used by the nav_state module family.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from platyplaty.ui.nav_listing import get_listing, get_selected_index

if TYPE_CHECKING:
    from platyplaty.ui.nav_state import NavigationState


def adjust_scroll(state: NavigationState, pane_height: int) -> None:
    """Adjust scroll_offset so the selected item is visible.

    Call this after any operation that changes selection to ensure
    the selected item remains visible within the pane.

    Args:
        state: The navigation state to update.
        pane_height: The height of the pane in lines. If zero or
            negative, this method does nothing.
    """
    if pane_height <= 0:
        return
    selected_index = get_selected_index(state)
    if selected_index is None:
        return
    listing = get_listing(state)
    item_count = len(listing.entries) if listing else 0
    _clamp_scroll_to_selection(state, selected_index, pane_height, item_count)


def calc_safe_zone_scroll(
    selected_index: int,
    scroll_offset: int,
    pane_height: int,
    item_count: int,
) -> int:
    """Calculate scroll offset using the safe-zone algorithm.

    This pure function implements the Safe-Zone Scroll Algorithm
    from the UI architecture. The selection can move freely within
    a comfortable viewing zone; scrolling occurs only when the
    selection approaches the edges.

    Args:
        selected_index: The index of the selected item.
        scroll_offset: The current scroll offset.
        pane_height: The height of the pane in lines.
        item_count: The total number of items in the listing.

    Returns:
        The adjusted scroll offset.
    """
    buffer = max(1, pane_height // 4)
    if 2 * buffer >= pane_height:
        offset = selected_index - pane_height // 2
    elif selected_index < scroll_offset + buffer:
        offset = selected_index - buffer
    elif selected_index > scroll_offset + pane_height - buffer - 1:
        offset = selected_index - pane_height + buffer + 1
    else:
        offset = scroll_offset
    offset = max(0, offset)
    max_offset = max(0, item_count - pane_height)
    return min(offset, max_offset)


def _clamp_scroll_to_selection(
    state: NavigationState,
    index: int,
    pane_height: int,
    item_count: int,
) -> None:
    """Clamp scroll_offset so index is visible within pane_height.

    Args:
        state: The navigation state to update.
        index: The selected item index.
        pane_height: The height of the pane in lines.
        item_count: The total number of items in the listing.
    """
    new_offset = calc_safe_zone_scroll(
        index, state.scroll_offset, pane_height, item_count
    )
    state.scroll_offset = new_offset
