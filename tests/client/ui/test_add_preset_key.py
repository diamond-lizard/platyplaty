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
            with patch("platyplaty.ui.file_browser_actions._autoplay_first_preset"):
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
            with patch("platyplaty.ui.file_browser_actions._autoplay_first_preset"):
                await action_add_preset_or_load_playlist(mock_browser)
        mock_browser.platyplaty_app.ctx.playlist.add_preset.assert_called_once_with(symlink)


class TestAutoplayOnAdd:
    """Tests for auto-play when adding to empty playlist."""
    
    @pytest.mark.asyncio
    async def test_adding_to_empty_playlist_triggers_autoplay(
        self, mock_browser: MagicMock, tmp_path: Path
    ) -> None:
        """Adding preset to empty playlist auto-plays it."""
        from platyplaty.ui.file_browser_actions import (
            action_add_preset_or_load_playlist,
        )
        milk_file = tmp_path / "test.milk"
        milk_file.write_text("content")
        entry = DirectoryEntry("test.milk", EntryType.FILE, milk_file)
        mock_browser.get_selected_entry.return_value = entry
        mock_browser.platyplaty_app.ctx.playlist.presets = []
        with patch("platyplaty.ui.file_browser_actions.is_readable", return_value=True):
            with patch("platyplaty.ui.file_browser_actions._autoplay_first_preset") as mock_auto:
                await action_add_preset_or_load_playlist(mock_browser)
        mock_auto.assert_called_once()

    @pytest.mark.asyncio
    async def test_adding_to_nonempty_playlist_no_autoplay(
        self, mock_browser: MagicMock, tmp_path: Path
    ) -> None:
        """Adding preset to non-empty playlist does not trigger autoplay."""
        from platyplaty.ui.file_browser_actions import (
            action_add_preset_or_load_playlist,
        )
        milk_file = tmp_path / "test.milk"
        milk_file.write_text("content")
        entry = DirectoryEntry("test.milk", EntryType.FILE, milk_file)
        mock_browser.get_selected_entry.return_value = entry
        mock_browser.platyplaty_app.ctx.playlist.presets = [Path("/existing.milk")]
        with patch("platyplaty.ui.file_browser_actions.is_readable", return_value=True):
            with patch("platyplaty.ui.file_browser_actions._autoplay_first_preset") as mock_auto:
                await action_add_preset_or_load_playlist(mock_browser)
        mock_auto.assert_not_called()

    @pytest.mark.asyncio
    async def test_adding_to_nonempty_playlist_selection_unchanged(
        self, mock_browser: MagicMock, tmp_path: Path
    ) -> None:
        """Adding preset to non-empty playlist does not change selection."""
        from platyplaty.ui.file_browser_actions import (
            action_add_preset_or_load_playlist,
        )
        milk_file = tmp_path / "test.milk"
        milk_file.write_text("content")
        entry = DirectoryEntry("test.milk", EntryType.FILE, milk_file)
        mock_browser.get_selected_entry.return_value = entry
        mock_browser.platyplaty_app.ctx.playlist.presets = [Path("/existing.milk")]
        mock_browser.platyplaty_app.ctx.playlist.selection_index = 0
        with patch("platyplaty.ui.file_browser_actions.is_readable", return_value=True):
            with patch("platyplaty.ui.file_browser_actions._autoplay_first_preset"):
                await action_add_preset_or_load_playlist(mock_browser)
        mock_browser.platyplaty_app.ctx.playlist.set_selection.assert_not_called()
