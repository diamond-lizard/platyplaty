"""Helper functions for left scroll after vertical navigation tests."""

from pathlib import Path
from unittest.mock import MagicMock

from platyplaty.ui.directory_types import DirectoryEntry, DirectoryListing, EntryType


def make_listing(entries: list[DirectoryEntry]) -> DirectoryListing:
    """Create a DirectoryListing from entries."""
    return DirectoryListing(
        entries=entries,
        was_empty=len(entries) == 0,
        had_filtered_entries=False,
        permission_denied=False,
    )


def make_large_left_listing(
    current_dir_index: int = 129,
    current_dir_name: str | None = None,
) -> tuple:
    """Create a large parent directory listing with 201 items.

    Returns (listing, current_dir_name, current_dir_index).
    The current directory is placed at the specified index.
    """
    entries = [
        DirectoryEntry(f"dir{i:03d}", EntryType.DIRECTORY, Path("/dummy"))
        for i in range(201)
    ]
    current_dir_name = current_dir_name or "current_dir"
    entries[current_dir_index] = DirectoryEntry(
        current_dir_name, EntryType.DIRECTORY, Path("/dummy")
    )
    return make_listing(entries), current_dir_name, current_dir_index


def make_small_middle_listing() -> DirectoryListing:
    """Create a small middle directory with 3 files."""
    entries = [
        DirectoryEntry("file1.milk", EntryType.FILE, Path("/dummy")),
        DirectoryEntry("file2.milk", EntryType.FILE, Path("/dummy")),
        DirectoryEntry("file3.milk", EntryType.FILE, Path("/dummy")),
    ]
    return make_listing(entries)


def make_mock_browser(
    left_listing: DirectoryListing,
    middle_listing: DirectoryListing,
    current_dir_name: str,
    left_scroll_offset: int = 0,
    middle_scroll_offset: int = 0,
    selected_index: int = 0,
):
    """Create a mock FileBrowser with specified attributes."""
    browser = MagicMock()
    browser._left_listing = left_listing
    browser._middle_listing = middle_listing
    browser._left_scroll_offset = left_scroll_offset
    browser._middle_scroll_offset = middle_scroll_offset
    browser.selected_index = selected_index
    browser.current_dir = MagicMock()
    browser.current_dir.name = current_dir_name
    browser.size = MagicMock()
    browser.size.height = 32  # 31 pane height + 1 path line
    browser.refresh = MagicMock()
    return browser


def setup_nav_state_mock(browser, middle_listing, parent_scroll: int = 0):
    """Configure browser._nav_state mock for navigation tests.

    Sets up all required mock return values for action_nav_down tests.
    """
    browser._nav_state = MagicMock()
    browser._nav_state.move_down.return_value = True
    browser._nav_state.current_dir = browser.current_dir
    browser._nav_state.get_listing.return_value = middle_listing
    browser._nav_state.get_selected_entry.return_value = middle_listing.entries[1]
    browser._nav_state.scroll_offset = 0
    browser._nav_state.get_parent_scroll_offset.return_value = parent_scroll
    browser._nav_state.adjust_scroll = MagicMock()


def is_index_visible(scroll_offset: int, pane_height: int, index: int) -> bool:
    """Check if a given index is visible within the scroll window."""
    visible_start = scroll_offset
    visible_end = visible_start + pane_height - 1
    return visible_start <= index <= visible_end
