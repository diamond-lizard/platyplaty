#!/usr/bin/env python3
"""Tests for left pane scroll adjustment.

This module tests the adjust_left_pane_scroll function that ensures
the current directory is visible in the left pane.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.directory_types import DirectoryEntry, DirectoryListing, EntryType
from platyplaty.ui.file_browser_scroll import adjust_left_pane_scroll


def make_listing(entries: list[DirectoryEntry]) -> DirectoryListing:
    """Create a DirectoryListing from entries."""
    return DirectoryListing(
        entries=entries,
        was_empty=len(entries) == 0,
        had_filtered_entries=False,
        permission_denied=False,
    )


def make_mock_browser(
    left_listing: DirectoryListing | None,
    current_dir_name: str,
    left_scroll_offset: int = 0,
):
    """Create a mock FileBrowser with specified attributes."""
    browser = MagicMock()
    browser._left_listing = left_listing
    browser._left_scroll_offset = left_scroll_offset
    browser.current_dir = MagicMock()
    browser.current_dir.name = current_dir_name
    return browser


class TestAdjustLeftPaneScroll:
    """Tests for adjust_left_pane_scroll function."""

    def test_zero_pane_height_no_change(self) -> None:
        """Zero pane height returns early without changing offset."""
        entries = [DirectoryEntry("current", EntryType.DIRECTORY, Path("/dummy"))]
        listing = make_listing(entries)
        browser = make_mock_browser(listing, "current", 5)
        adjust_left_pane_scroll(browser, 0)
        assert browser._left_scroll_offset == 5

    def test_negative_pane_height_no_change(self) -> None:
        """Negative pane height returns early without changing offset."""
        entries = [DirectoryEntry("current", EntryType.DIRECTORY, Path("/dummy"))]
        listing = make_listing(entries)
        browser = make_mock_browser(listing, "current", 5)
        adjust_left_pane_scroll(browser, -1)
        assert browser._left_scroll_offset == 5

    def test_none_listing_no_change(self) -> None:
        """None listing returns early without changing offset."""
        browser = make_mock_browser(None, "current", 5)
        adjust_left_pane_scroll(browser, 16)
        assert browser._left_scroll_offset == 5

    def test_empty_listing_no_change(self) -> None:
        """Empty listing returns early without changing offset."""
        listing = make_listing([])
        browser = make_mock_browser(listing, "current", 5)
        adjust_left_pane_scroll(browser, 16)
        assert browser._left_scroll_offset == 5

    def test_adjusts_when_selection_offscreen(self) -> None:
        """Adjusts scroll when selection would be off-screen."""
        # 50 entries, current dir is at index 40
        entries = [DirectoryEntry(f"dir{i}", EntryType.DIRECTORY, Path("/dummy")) for i in range(50)]
        entries[40] = DirectoryEntry("current", EntryType.DIRECTORY, Path("/dummy"))
        listing = make_listing(entries)
        # Scroll offset 0, pane height 16: visible range 0-15
        # Index 40 is not visible, should adjust
        browser = make_mock_browser(listing, "current", 0)
        adjust_left_pane_scroll(browser, 16)
        # After adjustment, index 40 should be visible
        assert browser._left_scroll_offset <= 40
        assert browser._left_scroll_offset + 16 > 40

    def test_idempotent_when_already_visible(self) -> None:
        """Returns same offset when selection is already visible."""
        entries = [DirectoryEntry(f"dir{i}", EntryType.DIRECTORY, Path("/dummy")) for i in range(20)]
        entries[5] = DirectoryEntry("current", EntryType.DIRECTORY, Path("/dummy"))
        listing = make_listing(entries)
        # Index 5 is visible with scroll_offset=0, pane_height=16
        browser = make_mock_browser(listing, "current", 0)
        adjust_left_pane_scroll(browser, 16)
        # Offset should remain 0 (or within safe zone constraints)
        assert browser._left_scroll_offset <= 5
        assert browser._left_scroll_offset + 16 > 5

    def test_item_not_found_uses_zero(self) -> None:
        """When current dir not found, index 0 is used."""
        entries = [DirectoryEntry(f"dir{i}", EntryType.DIRECTORY, Path("/dummy")) for i in range(10)]
        listing = make_listing(entries)
        browser = make_mock_browser(listing, "notfound", 5)
        adjust_left_pane_scroll(browser, 16)
        # find_entry_index returns 0 when not found, so offset adjusts for index 0
        assert browser._left_scroll_offset == 0
