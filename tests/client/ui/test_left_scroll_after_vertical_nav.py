#!/usr/bin/env python3
"""Tests for left pane scroll preservation after vertical navigation.

This module tests that after up/down navigation in the middle pane,
the left pane scroll offset is adjusted to keep the current directory
visible.

Regression test for bug: left pane scroll resets to 0 after up/down
navigation, making the current directory invisible when it was far
down in the parent directory listing.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.directory_types import DirectoryEntry, DirectoryListing, EntryType


def make_listing(entries: list[DirectoryEntry]) -> DirectoryListing:
    """Create a DirectoryListing from entries."""
    return DirectoryListing(
        entries=entries,
        was_empty=len(entries) == 0,
        had_filtered_entries=False,
        permission_denied=False,
    )


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


class TestLeftScrollAfterVerticalNav:
    """Tests for left pane scroll preservation after up/down navigation."""

    def test_left_scroll_preserved_after_sync_from_nav_state(self) -> None:
        """Left pane scroll should keep current directory visible after sync.

        This tests the bug where sync_from_nav_state() resets
        _left_scroll_offset to 0 (from parent memory), making the
        current directory invisible when it was far down in the list.

        The fix should call adjust_left_pane_scroll() after
        sync_from_nav_state() in up/down navigation.
        """
        from platyplaty.ui.file_browser_scroll import adjust_left_pane_scroll
        from platyplaty.ui.file_browser_sync import sync_from_nav_state

        # Create a large parent directory (201 items)
        # Current dir "platyplaty" is at index 129
        left_entries = [
            DirectoryEntry(f"dir{i:03d}", EntryType.DIRECTORY, Path("/dummy")) for i in range(201)
        ]
        left_entries[129] = DirectoryEntry("platyplaty", EntryType.DIRECTORY, Path("/dummy"))
        left_listing = make_listing(left_entries)

        # Create a small middle directory (just a few items)
        middle_entries = [
            DirectoryEntry("file1.milk", EntryType.FILE, Path("/dummy")),
            DirectoryEntry("file2.milk", EntryType.FILE, Path("/dummy")),
            DirectoryEntry("file3.milk", EntryType.FILE, Path("/dummy")),
        ]
        middle_listing = make_listing(middle_entries)

        # Create browser where current dir is far down in parent (index 129)
        # but scroll is set correctly to make it visible (e.g., 106)
        browser = make_mock_browser(
            left_listing=left_listing,
            middle_listing=middle_listing,
            current_dir_name="platyplaty",
            left_scroll_offset=106,  # Correct scroll to see index 129
            selected_index=0,
        )

        # First verify adjust_left_pane_scroll works correctly
        pane_height = 31
        adjust_left_pane_scroll(browser, pane_height)
        correct_scroll = browser._left_scroll_offset

        # Now simulate what sync_from_nav_state does: reset to 0
        # (simulating get_parent_scroll_offset returning 0)
        browser._left_scroll_offset = 0

        # The bug: after this reset, the current directory (index 129)
        # is no longer visible (scroll 0 shows indices 0-30)
        visible_start = browser._left_scroll_offset
        visible_end = visible_start + pane_height - 1
        current_dir_index = 129
        assert not (visible_start <= current_dir_index <= visible_end), \
            "Bug precondition: index 129 should NOT be visible with scroll=0"

        # The fix: call adjust_left_pane_scroll after sync
        adjust_left_pane_scroll(browser, pane_height)

        # Now verify current directory is visible
        visible_start = browser._left_scroll_offset
        visible_end = visible_start + pane_height - 1
        assert visible_start <= current_dir_index <= visible_end, \
            f"After fix: index {current_dir_index} should be visible " \
            f"(scroll={browser._left_scroll_offset}, visible={visible_start}-{visible_end})"

    @pytest.mark.asyncio
    async def test_action_nav_down_preserves_left_scroll(self) -> None:
        """action_nav_down should preserve left pane scroll visibility.

        This is a regression test: after pressing down in the middle pane,
        the current directory should remain visible in the left pane.
        The bug was that sync_from_nav_state reset _left_scroll_offset
        to 0 without re-adjusting it.
        """
        from platyplaty.ui.file_browser_nav_updown import action_nav_down
        from platyplaty.ui.file_browser_scroll import adjust_left_pane_scroll
        from platyplaty.ui.file_browser_sync import find_entry_index
        from platyplaty.ui.nav_state import NavigationState

        # Create a large parent directory (201 items)
        # Current dir "current_dir" is at index 129
        left_entries = [
            DirectoryEntry(f"dir{i:03d}", EntryType.DIRECTORY, Path("/dummy")) for i in range(201)
        ]
        left_entries[129] = DirectoryEntry("current_dir", EntryType.DIRECTORY, Path("/dummy"))
        left_listing = make_listing(left_entries)

        # Create middle directory with items to navigate
        middle_entries = [
            DirectoryEntry("file1.milk", EntryType.FILE, Path("/dummy")),
            DirectoryEntry("file2.milk", EntryType.FILE, Path("/dummy")),
            DirectoryEntry("file3.milk", EntryType.FILE, Path("/dummy")),
        ]
        middle_listing = make_listing(middle_entries)

        # Create mock browser
        browser = make_mock_browser(
            left_listing=left_listing,
            middle_listing=middle_listing,
            current_dir_name="current_dir",
            left_scroll_offset=106,  # Correct scroll to see index 129
            selected_index=0,  # At first item in middle pane
        )

        # Mock NavigationState
        browser._nav_state = MagicMock()
        browser._nav_state.move_down.return_value = True
        browser._nav_state.current_dir = browser.current_dir
        browser._nav_state.get_listing.return_value = middle_listing
        browser._nav_state.get_selected_entry.return_value = middle_entries[1]
        browser._nav_state.scroll_offset = 0
        browser._nav_state.get_parent_scroll_offset.return_value = 0  # Bug trigger
        browser._nav_state.adjust_scroll = MagicMock()

        pane_height = 31
        current_dir_index = 129

        # Verify precondition: current dir is visible before nav
        adjust_left_pane_scroll(browser, pane_height)
        visible_start = browser._left_scroll_offset
        visible_end = visible_start + pane_height - 1
        assert visible_start <= current_dir_index <= visible_end, \
            "Precondition: current dir should be visible initially"

        # Patch make_file_preview to avoid mock path issues
        with patch(
            "platyplaty.ui.file_browser_refresh.make_file_preview",
            return_value=None,
        ):
            await action_nav_down(browser)

        # After navigation, current dir should STILL be visible
        visible_start = browser._left_scroll_offset
        visible_end = visible_start + pane_height - 1
        assert visible_start <= current_dir_index <= visible_end, \
            f"After nav_down: index {current_dir_index} should be visible " \
            f"(scroll={browser._left_scroll_offset}, visible={visible_start}-{visible_end})"
