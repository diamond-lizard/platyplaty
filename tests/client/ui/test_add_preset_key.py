#!/usr/bin/env python3
"""Tests for 'a' key behavior on different file types in file browser.

This module tests the action_add_preset_or_load_playlist function
which handles the 'a' key in the file browser section.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.directory_types import DirectoryEntry, EntryType


@pytest.fixture
def mock_browser() -> MagicMock:
    """Create a mock FileBrowser for testing."""
    browser = MagicMock()
    browser.platyplaty_app = MagicMock()
    browser.platyplaty_app.ctx = MagicMock()
    browser.platyplaty_app.ctx.playlist = MagicMock()
    browser.platyplaty_app.ctx.playlist.presets = []
    return browser


class TestAddMilkPreset:
    """Tests for adding .milk files to playlist."""

    @pytest.mark.asyncio
    async def test_milk_file_added_to_playlist(
        self, mock_browser: MagicMock, tmp_path: Path
    ) -> None:
        """'a' on readable .milk file adds it to playlist."""
        from platyplaty.ui.file_browser_actions import (
            action_add_preset_or_load_playlist,
        )
        milk_file = tmp_path / "test.milk"
        milk_file.write_text("preset content")
        entry = DirectoryEntry("test.milk", EntryType.FILE, milk_file)
        mock_browser.get_selected_entry.return_value = entry
        mock_browser.platyplaty_app.ctx.playlist.presets = []
        with patch("platyplaty.ui.file_browser_actions.is_readable", return_value=True):
            with patch("platyplaty.ui.file_browser_actions.autoplay_first_preset"):
                await action_add_preset_or_load_playlist(mock_browser)
        mock_browser.platyplaty_app.ctx.playlist.add_preset.assert_called_once_with(milk_file)

    @pytest.mark.asyncio
    async def test_symlink_to_milk_added(
        self, mock_browser: MagicMock, tmp_path: Path
    ) -> None:
        """'a' on symlink to .milk file adds the symlink path."""
        from platyplaty.ui.file_browser_actions import (
            action_add_preset_or_load_playlist,
        )
        target = tmp_path / "target.milk"
        target.write_text("content")
        symlink = tmp_path / "link.milk"
        symlink.symlink_to(target)
        entry = DirectoryEntry("link.milk", EntryType.SYMLINK_TO_FILE, symlink)
        mock_browser.get_selected_entry.return_value = entry
        mock_browser.platyplaty_app.ctx.playlist.presets = []
        with patch("platyplaty.ui.file_browser_actions.is_readable", return_value=True):
            with patch("platyplaty.ui.file_browser_actions.autoplay_first_preset"):
                await action_add_preset_or_load_playlist(mock_browser)
        mock_browser.platyplaty_app.ctx.playlist.add_preset.assert_called_once_with(symlink)

