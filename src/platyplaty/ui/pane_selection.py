"""Selection helpers for the Pane widget.

This module provides functions for accessing selected entries in a pane,
extracted to reduce file size in the Pane class.
"""

from platyplaty.ui.directory_types import DirectoryEntry


def get_selected_entry(
    entries: list[DirectoryEntry],
    selected_index: int,
) -> DirectoryEntry | None:
    """Get the currently selected entry.

    Args:
        entries: List of directory entries.
        selected_index: Index of the currently selected entry.

    Returns:
        The selected DirectoryEntry, or None if index is invalid.
    """
    if selected_index < 0 or selected_index >= len(entries):
        return None
    return entries[selected_index]


def get_selected_name(
    entries: list[DirectoryEntry],
    selected_index: int,
) -> str | None:
    """Get the name of the currently selected entry.

    Args:
        entries: List of directory entries.
        selected_index: Index of the currently selected entry.

    Returns:
        The name of the selected entry, or None if index is invalid.
    """
    entry = get_selected_entry(entries, selected_index)
    return entry.name if entry else None
