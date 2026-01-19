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

from conftest import make_listing
from platyplaty.ui.directory_types import DirectoryEntry, EntryType

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
        with patch("platyplaty.ui.file_browser_preset_preview._preview_milk_preset"):
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
        with patch("platyplaty.ui.file_browser_preset_preview._preview_milk_preset"):
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
        with patch("platyplaty.ui.file_browser_preset_preview._preview_milk_preset"):
            await action_play_next_preset(mock_browser)
        assert mock_browser._state.selected_index == 2
