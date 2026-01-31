"""Query functions for navigation state memory.

This module provides read-only query functions for looking up
remembered selection and scroll position for directories.
These are package-private functions used by the nav_state module family.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.ui.nav_state import NavigationState


def get_scroll_offset_for_directory(
    state: NavigationState,
    directory_path: str,
) -> int:
    """Get the remembered scroll offset for a directory.

    Args:
        state: The navigation state to query.
        directory_path: The directory path to look up.

    Returns:
        The remembered scroll offset, or 0 if not remembered.
    """
    memory = state._directory_memory.get(directory_path)
    if memory:
        return memory.scroll_offset
    return 0


def get_selected_name_for_directory(
    state: NavigationState,
    directory_path: str,
) -> str | None:
    """Get the remembered selected name for a directory.

    Args:
        state: The navigation state to query.
        directory_path: The directory path to look up.

    Returns:
        The remembered selected name, or None if not remembered.
    """
    memory = state._directory_memory.get(directory_path)
    if memory:
        return memory.selected_name
    return None


def get_parent_scroll_offset(state: NavigationState, current_dir: Path) -> int:
    """Get the remembered scroll offset for the parent directory.

    Args:
        state: The navigation state to query.
        current_dir: The current directory path.

    Returns:
        The scroll offset for the parent directory, or 0 if not remembered.
    """
    parent = current_dir.parent
    if parent == current_dir:
        return 0
    return get_scroll_offset_for_directory(state, str(parent.resolve()))
