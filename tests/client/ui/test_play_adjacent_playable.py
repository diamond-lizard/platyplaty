#!/usr/bin/env python3
"""Tests for playable entries and K boundary behavior.

This module tests that symlinks to .milk files are playable and
K is a no-op at the first position.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from conftest import make_listing
from platyplaty.ui.directory_types import DirectoryEntry, EntryType

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
        with patch("platyplaty.ui.file_browser_preset_preview._preview_milk_preset"):
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
        with patch("platyplaty.ui.file_browser_preset_preview._preview_milk_preset") as mock_prev:
            await action_play_previous_preset(mock_browser)
        mock_prev.assert_not_called()
        assert mock_browser._state.selected_index == 0
