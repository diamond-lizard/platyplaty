#!/usr/bin/env python3
"""Tests for J/K skipping over non-.milk entries.

This module tests that J/K skip over .platy files, symlinks to
directories, and broken symlinks.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.directory_types import DirectoryEntry, DirectoryListing, EntryType


def make_listing(entries: list) -> DirectoryListing:
    """Create a DirectoryListing from a list of entries."""
    return DirectoryListing(
        entries=entries,
        was_empty=False,
        had_filtered_entries=False,
        permission_denied=False,
    )


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


class TestSkipPlatyFiles:
    """Tests for J/K skipping over .platy files."""

    @pytest.mark.asyncio
    async def test_next_skips_platy_file(self, mock_browser: MagicMock) -> None:
        """J skips .platy files to find next .milk file."""
        from platyplaty.ui.file_browser_play_actions import action_play_next_preset
        entries = [
            DirectoryEntry("a.milk", EntryType.FILE, Path("/a.milk")),
            DirectoryEntry("playlist.platy", EntryType.FILE, Path("/playlist.platy")),
            DirectoryEntry("b.milk", EntryType.FILE, Path("/b.milk")),
        ]
        mock_browser._state = MagicMock()
        mock_browser._state.listing = make_listing(entries)
        mock_browser._state.selected_index = 0
        mock_browser.get_selected_entry.return_value = entries[2]
        with patch("platyplaty.ui.file_browser_play_actions._preview_milk_preset"):
            await action_play_next_preset(mock_browser)
        assert mock_browser._state.selected_index == 2


class TestSkipSymlinkToDir:
    """Tests for J/K skipping over symlinks to directories."""

    @pytest.mark.asyncio
    async def test_next_skips_symlink_to_dir(
        self, mock_browser: MagicMock
    ) -> None:
        """J skips symlinks to directories."""
        from platyplaty.ui.file_browser_play_actions import action_play_next_preset
        entries = [
            DirectoryEntry("a.milk", EntryType.FILE, Path("/a.milk")),
            DirectoryEntry("link", EntryType.SYMLINK_TO_DIRECTORY, Path("/link")),
            DirectoryEntry("b.milk", EntryType.FILE, Path("/b.milk")),
        ]
        mock_browser._state = MagicMock()
        mock_browser._state.listing = make_listing(entries)
        mock_browser._state.selected_index = 0
        mock_browser.get_selected_entry.return_value = entries[2]
        with patch("platyplaty.ui.file_browser_play_actions._preview_milk_preset"):
            await action_play_next_preset(mock_browser)
        assert mock_browser._state.selected_index == 2


class TestSkipBrokenSymlink:
    """Tests for J/K skipping over broken symlinks."""

    @pytest.mark.asyncio
    async def test_next_skips_broken_symlink(
        self, mock_browser: MagicMock
    ) -> None:
        """J skips broken symlinks."""
        from platyplaty.ui.file_browser_play_actions import action_play_next_preset
        entries = [
            DirectoryEntry("a.milk", EntryType.FILE, Path("/a.milk")),
            DirectoryEntry("broken.milk", EntryType.BROKEN_SYMLINK, Path("/broken")),
            DirectoryEntry("b.milk", EntryType.FILE, Path("/b.milk")),
        ]
        mock_browser._state = MagicMock()
        mock_browser._state.listing = make_listing(entries)
        mock_browser._state.selected_index = 0
        mock_browser.get_selected_entry.return_value = entries[2]
        with patch("platyplaty.ui.file_browser_play_actions._preview_milk_preset"):
            await action_play_next_preset(mock_browser)
        assert mock_browser._state.selected_index == 2


class TestSymlinkToMilkPlayable:
    """Tests for symlinks to .milk files being playable."""

    @pytest.mark.asyncio
    async def test_symlink_to_milk_is_playable(
        self, mock_browser: MagicMock
    ) -> None:
        """J finds symlink to .milk file as next playable."""
        from platyplaty.ui.file_browser_play_actions import action_play_next_preset
        entries = [
            DirectoryEntry("a.milk", EntryType.FILE, Path("/a.milk")),
            DirectoryEntry("link.milk", EntryType.SYMLINK_TO_FILE, Path("/link.milk")),
        ]
        mock_browser._state = MagicMock()
        mock_browser._state.listing = make_listing(entries)
        mock_browser._state.selected_index = 0
        mock_browser.get_selected_entry.return_value = entries[1]
        with patch("platyplaty.ui.file_browser_play_actions._preview_milk_preset"):
            await action_play_next_preset(mock_browser)
        assert mock_browser._state.selected_index == 1


class TestKNoopAtFirst:
    """Tests for K being no-op at first position."""

    @pytest.mark.asyncio
    async def test_previous_noop_at_first_milk(
        self, mock_browser: MagicMock
    ) -> None:
        """K is no-op when at first .milk file."""
        from platyplaty.ui.file_browser_play_actions import action_play_previous_preset
        entries = [
            DirectoryEntry("a.milk", EntryType.FILE, Path("/a.milk")),
            DirectoryEntry("subdir", EntryType.DIRECTORY, Path("/subdir")),
        ]
        mock_browser._state = MagicMock()
        mock_browser._state.listing = make_listing(entries)
        mock_browser._state.selected_index = 0
        with patch("platyplaty.ui.file_browser_play_actions._preview_milk_preset") as mock_prev:
            await action_play_previous_preset(mock_browser)
        mock_prev.assert_not_called()
        assert mock_browser._state.selected_index == 0
