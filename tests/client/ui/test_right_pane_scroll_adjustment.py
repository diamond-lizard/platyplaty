#!/usr/bin/env python3
"""Tests for right pane scroll adjustment.

This module tests the adjust_right_pane_scroll function that ensures
the selection is visible in the right pane when showing directory contents.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.directory_types import DirectoryEntry, DirectoryListing, EntryType
from platyplaty.ui.file_browser_sync import adjust_right_pane_scroll
from platyplaty.ui.file_browser_types import RightPaneDirectory, RightPaneFilePreview


def make_listing(entries: list[DirectoryEntry]) -> DirectoryListing:
    """Create a DirectoryListing from entries."""
    return DirectoryListing(
        entries=entries,
        was_empty=len(entries) == 0,
        had_filtered_entries=False,
        permission_denied=False,
    )


def make_mock_browser(
    right_content,
    right_selected_index: int | None,
    right_scroll_offset: int = 0,
):
    """Create a mock FileBrowser with specified attributes."""
    browser = MagicMock()
    browser._right_content = right_content
    browser._right_selected_index = right_selected_index
    browser._right_scroll_offset = right_scroll_offset
    return browser


class TestAdjustRightPaneScroll:
    """Tests for adjust_right_pane_scroll function."""

    def test_zero_pane_height_no_change(self) -> None:
        """Zero pane height returns early without changing offset."""
        entries = [DirectoryEntry("file.milk", EntryType.FILE)]
        listing = make_listing(entries)
        content = RightPaneDirectory(listing)
        browser = make_mock_browser(content, 0, 5)
        adjust_right_pane_scroll(browser, 0)
        assert browser._right_scroll_offset == 5

    def test_negative_pane_height_no_change(self) -> None:
        """Negative pane height returns early without changing offset."""
        entries = [DirectoryEntry("file.milk", EntryType.FILE)]
        listing = make_listing(entries)
        content = RightPaneDirectory(listing)
        browser = make_mock_browser(content, 0, 5)
        adjust_right_pane_scroll(browser, -1)
        assert browser._right_scroll_offset == 5

    def test_none_selected_index_no_change(self) -> None:
        """None selected_index (file preview) returns early without changing offset."""
        content = RightPaneFilePreview(["line1", "line2"])
        browser = make_mock_browser(content, None, 5)
        adjust_right_pane_scroll(browser, 16)
        assert browser._right_scroll_offset == 5

    def test_none_content_no_change(self) -> None:
        """None content returns early without changing offset."""
        browser = make_mock_browser(None, 0, 5)
        adjust_right_pane_scroll(browser, 16)
        assert browser._right_scroll_offset == 5

    def test_file_preview_content_no_change(self) -> None:
        """File preview content returns early without changing offset."""
        content = RightPaneFilePreview(["line1", "line2"])
        browser = make_mock_browser(content, 0, 5)
        adjust_right_pane_scroll(browser, 16)
        assert browser._right_scroll_offset == 5

    def test_empty_listing_no_change(self) -> None:
        """Empty listing returns early without changing offset."""
        listing = make_listing([])
        content = RightPaneDirectory(listing)
        browser = make_mock_browser(content, 0, 5)
        adjust_right_pane_scroll(browser, 16)
        assert browser._right_scroll_offset == 5

    def test_adjusts_when_selection_offscreen(self) -> None:
        """Adjusts scroll when selection would be off-screen."""
        entries = [DirectoryEntry(f"file{i}.milk", EntryType.FILE) for i in range(50)]
        listing = make_listing(entries)
        content = RightPaneDirectory(listing)
        browser = make_mock_browser(content, 40, 0)
        adjust_right_pane_scroll(browser, 16)
        assert browser._right_scroll_offset <= 40
        assert browser._right_scroll_offset + 16 > 40

    def test_idempotent_when_already_visible(self) -> None:
        """Returns same offset when selection is already visible."""
        entries = [DirectoryEntry(f"file{i}.milk", EntryType.FILE) for i in range(20)]
        listing = make_listing(entries)
        content = RightPaneDirectory(listing)
        browser = make_mock_browser(content, 5, 0)
        adjust_right_pane_scroll(browser, 16)
        assert browser._right_scroll_offset <= 5
        assert browser._right_scroll_offset + 16 > 5
