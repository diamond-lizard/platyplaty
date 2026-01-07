"""Navigation types and helper functions.

This module provides the DirectoryMemory dataclass and helper functions
for finding entries in directory listings. These are used by the
navigation state module family (nav_state, nav_moves, nav_memory, nav_listing).
"""

from dataclasses import dataclass

from platyplaty.ui.directory_types import DirectoryListing


@dataclass
class DirectoryMemory:
    """Remembered state for a directory.

    Attributes:
        selected_name: The name of the selected item.
        scroll_offset: The scroll offset in the pane.
    """

    selected_name: str | None = None
    scroll_offset: int = 0


def find_name_in_listing(listing: DirectoryListing, name: str) -> bool:
    """Check if a name exists in a directory listing.

    Args:
        listing: The directory listing to search.
        name: The name to find.

    Returns:
        True if the name exists in the listing.
    """
    return any(entry.name == name for entry in listing.entries)


def find_index_by_name(listing: DirectoryListing, name: str) -> int | None:
    """Find the index of an entry by name.

    Args:
        listing: The directory listing to search.
        name: The name to find.

    Returns:
        The index of the entry, or None if not found.
    """
    for i, entry in enumerate(listing.entries):
        if entry.name == name:
            return i
    return None
