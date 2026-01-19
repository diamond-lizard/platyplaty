#!/usr/bin/env python3
"""Tests for 'a' key error cases in file browser.

This module tests error cases when the 'a' key is pressed on
directories, broken symlinks, or unreadable files.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.directory_types import DirectoryEntry, EntryType


@pytest.fixture
def mock_browser() -> MagicMock:
    """Create a mock FileBrowser for testing."""
    browser = MagicMock()
    browser.app = MagicMock()
    browser.app.ctx = MagicMock()
    browser.app.ctx.playlist = MagicMock()
    browser.app.ctx.playlist.presets = []
    return browser


class TestAddPresetErrors:
    """Tests for 'a' key error cases."""

    @pytest.mark.asyncio
    async def test_directory_shows_error(self, mock_browser: MagicMock) -> None:
        """'a' on directory shows error message."""
        from platyplaty.ui.file_browser_actions import (
            action_add_preset_or_load_playlist,
        )
        entry = DirectoryEntry("subdir", EntryType.DIRECTORY, Path("/test/subdir"))
        mock_browser.get_selected_entry.return_value = entry
        with patch("platyplaty.ui.file_browser_actions.show_transient_error") as mock_err:
            await action_add_preset_or_load_playlist(mock_browser)
        mock_err.assert_called_once()
        assert "not a playlist or preset" in mock_err.call_args[0][1]

    @pytest.mark.asyncio
    async def test_symlink_to_dir_shows_error(self, mock_browser: MagicMock) -> None:
        """'a' on symlink to directory shows error message."""
        from platyplaty.ui.file_browser_actions import (
            action_add_preset_or_load_playlist,
        )
        entry = DirectoryEntry("link", EntryType.SYMLINK_TO_DIRECTORY, Path("/link"))
        mock_browser.get_selected_entry.return_value = entry
        with patch("platyplaty.ui.file_browser_actions.show_transient_error") as mock_err:
            await action_add_preset_or_load_playlist(mock_browser)
        mock_err.assert_called_once()
        assert "not a playlist or preset" in mock_err.call_args[0][1]

    @pytest.mark.asyncio
    async def test_broken_symlink_shows_error(self, mock_browser: MagicMock) -> None:
        """'a' on broken symlink shows error message."""
        from platyplaty.ui.file_browser_actions import (
            action_add_preset_or_load_playlist,
        )
        entry = DirectoryEntry("broken.milk", EntryType.BROKEN_SYMLINK, Path("/broken"))
        mock_browser.get_selected_entry.return_value = entry
        with patch("platyplaty.ui.file_browser_actions.show_transient_error") as mock_err:
            await action_add_preset_or_load_playlist(mock_browser)
        mock_err.assert_called_once()
        assert "not a playlist or preset" in mock_err.call_args[0][1]

    @pytest.mark.asyncio
    async def test_unreadable_milk_shows_error(self, mock_browser: MagicMock) -> None:
        """'a' on unreadable .milk file shows error message."""
        from platyplaty.ui.file_browser_actions import (
            action_add_preset_or_load_playlist,
        )
        entry = DirectoryEntry("test.milk", EntryType.FILE, Path("/test.milk"))
        mock_browser.get_selected_entry.return_value = entry
        with patch("platyplaty.ui.file_browser_actions.is_readable", return_value=False):
            with patch("platyplaty.ui.file_browser_actions.show_transient_error") as mock_err:
                await action_add_preset_or_load_playlist(mock_browser)
        mock_err.assert_called_once()
        assert "not readable" in mock_err.call_args[0][1]
