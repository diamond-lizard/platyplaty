"""Left navigation for navigation state.

This module provides the move_left function for navigating to the
parent directory. This is a package-private function used by
the nav_state module family.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from platyplaty.ui.indicator_cache import refresh_indicator_cache
from platyplaty.ui.nav_access import check_directory_accessible
from platyplaty.ui.nav_listing import get_selected_entry, refresh_listing
from platyplaty.ui.nav_memory import (
    restore_scroll_from_memory,
    save_current_memory,
)

if TYPE_CHECKING:
    from platyplaty.ui.nav_state import NavigationState


def move_left(state: NavigationState) -> bool:
    """Navigate to parent directory.

    No-op if at filesystem root. Saves current memory before navigating.

    Args:
        state: The navigation state to update.

    Returns:
        True if navigated, False if at root.

    Raises:
        InaccessibleDirectoryError: If parent directory cannot be accessed.
    """
    parent = state.current_dir.parent
    if parent == state.current_dir:
        return False
    check_directory_accessible(parent)
    save_current_memory(state)
    came_from = state.current_dir.name
    state.current_dir = parent
    refresh_listing(state)
    state.selected_name = came_from
    restore_scroll_from_memory(state)
    entry = get_selected_entry(state)
    if entry is not None:
        refresh_indicator_cache(entry.entry_type, entry.path)
    return True
