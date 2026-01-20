#!/usr/bin/env python3
"""Tests for J/K play previous/next preset in file browser.

This module tests the action_play_previous_preset and
action_play_next_preset functions (J/K keys).
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.directory_types import DirectoryEntry, DirectoryListing, EntryType


def make_listing(entries: list) -> DirectoryListing:
    """Create a DirectoryListing from a list of entries."""
    return DirectoryListing(entries=entries, was_empty=False, had_filtered_entries=False, permission_denied=False)


@pytest.fixture
def mock_browser() -> MagicMock:
    """Create a mock FileBrowser for testing."""
    browser = MagicMock()
    browser.app = MagicMock()
    browser.app.ctx = MagicMock()
    browser.app.ctx.playlist = MagicMock()
    browser.app.ctx.autoplay_manager = MagicMock()
    browser._adjust_scroll = MagicMock()
    browser.refresh = MagicMock()
    return browser


class TestPlayNextPreset:
    """Tests for J (play next preset) key."""

    @pytest.mark.asyncio
    async def test_skips_to_next_milk_file(self, mock_browser: MagicMock) -> None:
        """J skips directories and finds next .milk file."""
        from platyplaty.ui.file_browser_play_actions import action_play_next_preset
        entries = [
            DirectoryEntry("a.milk", EntryType.FILE, Path("/a.milk")),
            DirectoryEntry("subdir", EntryType.DIRECTORY, Path("/subdir")),
            DirectoryEntry("b.milk", EntryType.FILE, Path("/b.milk")),
        ]
        mock_browser.selected_index = 0
        mock_browser._middle_listing = make_listing(entries)
        mock_browser._nav_state = MagicMock()
        mock_browser._nav_state.scroll_offset = 0
        mock_browser.size = MagicMock()
        mock_browser.size.height = 20
        mock_browser.get_selected_entry.return_value = entries[2]
        with patch("platyplaty.ui.file_browser_preset_preview._preview_milk_preset"):
            await action_play_next_preset(mock_browser)
        assert mock_browser.selected_index == 2

    @pytest.mark.asyncio
    async def test_noop_when_no_more_milk_files(self, mock_browser: MagicMock) -> None:
        """J is no-op when at last .milk file."""
        from platyplaty.ui.file_browser_play_actions import action_play_next_preset
        entries = [
            DirectoryEntry("a.milk", EntryType.FILE, Path("/a.milk")),
            DirectoryEntry("subdir", EntryType.DIRECTORY, Path("/subdir")),
        ]
        mock_browser.selected_index = 0
        mock_browser._middle_listing = make_listing(entries)
        mock_browser._nav_state = MagicMock()
        mock_browser._nav_state.scroll_offset = 0
        mock_browser.size = MagicMock()
        mock_browser.size.height = 20
        with patch("platyplaty.ui.file_browser_preset_preview._preview_milk_preset") as mock_prev:
            await action_play_next_preset(mock_browser)
        mock_prev.assert_not_called()
        assert mock_browser.selected_index == 0


class TestPlayPreviousPreset:
    """Tests for K (play previous preset) key."""
    
    @pytest.mark.asyncio
    async def test_skips_to_previous_milk_file(self, mock_browser: MagicMock) -> None:
        """K skips directories and finds previous .milk file."""
        from platyplaty.ui.file_browser_play_actions import action_play_previous_preset
        entries = [
            DirectoryEntry("a.milk", EntryType.FILE, Path("/a.milk")),
            DirectoryEntry("subdir", EntryType.DIRECTORY, Path("/subdir")),
            DirectoryEntry("b.milk", EntryType.FILE, Path("/b.milk")),
        ]
        mock_browser.selected_index = 2
        mock_browser._middle_listing = make_listing(entries)
        mock_browser._nav_state = MagicMock()
        mock_browser._nav_state.scroll_offset = 0
        mock_browser.size = MagicMock()
        mock_browser.size.height = 20
        mock_browser.get_selected_entry.return_value = entries[0]
        with patch("platyplaty.ui.file_browser_preset_preview._preview_milk_preset"):
            await action_play_previous_preset(mock_browser)
        assert mock_browser.selected_index == 0
