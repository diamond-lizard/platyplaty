"""Scroll adjustment for navigation state.

This module provides functions for adjusting scroll position
to keep the selected item visible. This is a package-private
function used by the nav_state module family.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from platyplaty.ui.nav_listing import get_selected_index

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
    _clamp_scroll_to_selection(state, selected_index, pane_height)


def _clamp_scroll_to_selection(
    state: NavigationState,
    index: int,
    pane_height: int,
) -> None:
    """Clamp scroll_offset so index is visible within pane_height.

    Args:
        state: The navigation state to update.
        index: The selected item index.
        pane_height: The height of the pane in lines.
    """
    if index < state.scroll_offset:
        state.scroll_offset = index
        return
    visible_end = state.scroll_offset + pane_height
    if index >= visible_end:
        state.scroll_offset = index - pane_height + 1
