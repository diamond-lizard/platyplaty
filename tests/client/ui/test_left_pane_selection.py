#!/usr/bin/env python3
"""Tests for left pane selection index calculation.

This module tests _calc_left_selected_index() which finds the current
directory's position in the parent directory listing.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.directory_types import DirectoryEntry, DirectoryListing, EntryType
from platyplaty.ui.file_browser_render import _calc_left_selected_index


def make_listing(entries: list[DirectoryEntry]) -> DirectoryListing:
    """Create a DirectoryListing from entries."""
    return DirectoryListing(
        entries=entries,
        was_empty=len(entries) == 0,
        had_filtered_entries=False,
        permission_denied=False,
    )


def make_mock_browser(left_listing, current_dir_name: str):
    """Create a mock FileBrowser with specified attributes."""
    browser = MagicMock()
    browser._left_listing = left_listing
    browser.current_dir = MagicMock()
    browser.current_dir.name = current_dir_name
    return browser


class TestCalcLeftSelectedIndex:
    """Tests for _calc_left_selected_index function."""

    def test_finds_current_dir_at_first_position(self) -> None:
        """Returns 0 when current dir is first in parent listing."""
        entries = [
            DirectoryEntry("current", EntryType.DIRECTORY),
            DirectoryEntry("other", EntryType.DIRECTORY),
        ]
        listing = make_listing(entries)
        browser = make_mock_browser(listing, "current")
        assert _calc_left_selected_index(browser) == 0

    def test_finds_current_dir_at_middle_position(self) -> None:
        """Returns correct index when current dir is in middle."""
        entries = [
            DirectoryEntry("aaa", EntryType.DIRECTORY),
            DirectoryEntry("bbb", EntryType.DIRECTORY),
            DirectoryEntry("current", EntryType.DIRECTORY),
            DirectoryEntry("ddd", EntryType.DIRECTORY),
        ]
        listing = make_listing(entries)
        browser = make_mock_browser(listing, "current")
        assert _calc_left_selected_index(browser) == 2

    def test_finds_current_dir_at_last_position(self) -> None:
        """Returns last index when current dir is last in listing."""
        entries = [
            DirectoryEntry("aaa", EntryType.DIRECTORY),
            DirectoryEntry("zzz", EntryType.DIRECTORY),
        ]
        listing = make_listing(entries)
        browser = make_mock_browser(listing, "zzz")
        assert _calc_left_selected_index(browser) == 1

    def test_returns_none_when_listing_is_none(self) -> None:
        """Returns None when left listing is None (e.g., at root)."""
        browser = make_mock_browser(None, "current")
        assert _calc_left_selected_index(browser) is None

    def test_returns_none_when_listing_is_empty(self) -> None:
        """Returns None when left listing has no entries."""
        listing = make_listing([])
        browser = make_mock_browser(listing, "current")
        assert _calc_left_selected_index(browser) is None

    def test_returns_none_when_current_dir_not_found(self) -> None:
        """Returns None when current dir name not in listing."""
        entries = [
            DirectoryEntry("other1", EntryType.DIRECTORY),
            DirectoryEntry("other2", EntryType.DIRECTORY),
        ]
        listing = make_listing(entries)
        browser = make_mock_browser(listing, "missing")
        assert _calc_left_selected_index(browser) is None
