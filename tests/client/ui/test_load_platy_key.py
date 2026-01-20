#!/usr/bin/env python3
"""Tests for 'a' key loading .platy playlist files in file browser.

This module tests the _handle_load_platy_playlist function which
handles loading playlist files when 'a' is pressed on a .platy file.
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


class TestLoadPlatyFile:
    """Tests for loading .platy files via 'a' key."""

    @pytest.mark.asyncio
    async def test_platy_file_loads_playlist(
        self, mock_browser: MagicMock, tmp_path: Path
    ) -> None:
        """'a' on readable .platy file loads the playlist."""
        from platyplaty.ui.file_browser_actions import (
            action_add_preset_or_load_playlist,
        )
        platy_file = tmp_path / "test.platy"
        platy_file.write_text("/path/to/preset.milk\n")
        entry = DirectoryEntry("test.platy", EntryType.FILE, platy_file)
        mock_browser.get_selected_entry.return_value = entry
        with patch("platyplaty.ui.file_browser_actions.is_readable", return_value=True):
            with patch("platyplaty.playlist_snapshot.push_undo_snapshot"):
                with patch(
                    "platyplaty.commands.load_helpers.perform_load",
                    new_callable=AsyncMock,
                    return_value=(True, None),
                ) as mock_load:
                    await action_add_preset_or_load_playlist(mock_browser)
        mock_load.assert_called_once()
        assert mock_load.call_args[0][0] == platy_file

    @pytest.mark.asyncio
    async def test_symlink_to_platy_loads_playlist(
        self, mock_browser: MagicMock, tmp_path: Path
    ) -> None:
        """'a' on symlink to .platy file loads the playlist."""
        from platyplaty.ui.file_browser_actions import (
            action_add_preset_or_load_playlist,
        )
        target = tmp_path / "target.platy"
        target.write_text("/path/to/preset.milk\n")
        symlink = tmp_path / "link.platy"
        symlink.symlink_to(target)
        entry = DirectoryEntry("link.platy", EntryType.SYMLINK_TO_FILE, symlink)
        mock_browser.get_selected_entry.return_value = entry
        with patch("platyplaty.ui.file_browser_actions.is_readable", return_value=True):
            with patch("platyplaty.playlist_snapshot.push_undo_snapshot"):
                with patch(
                    "platyplaty.commands.load_helpers.perform_load",
                    new_callable=AsyncMock,
                    return_value=(True, None),
                ) as mock_load:
                    await action_add_preset_or_load_playlist(mock_browser)
        mock_load.assert_called_once()
        assert mock_load.call_args[0][0] == symlink


class TestLoadPlatyUndo:
    """Tests for undo snapshot on playlist load."""

    @pytest.mark.asyncio
    async def test_undo_snapshot_pushed_before_load(
        self, mock_browser: MagicMock, tmp_path: Path
    ) -> None:
        """Undo snapshot is pushed before loading playlist."""
        from platyplaty.ui.file_browser_actions import (
            action_add_preset_or_load_playlist,
        )
        platy_file = tmp_path / "test.platy"
        platy_file.write_text("/preset.milk\n")
        entry = DirectoryEntry("test.platy", EntryType.FILE, platy_file)
        mock_browser.get_selected_entry.return_value = entry
        with patch("platyplaty.ui.file_browser_actions.is_readable", return_value=True):
            with patch(
                "platyplaty.playlist_snapshot.push_undo_snapshot"
            ) as mock_undo:
                with patch(
                    "platyplaty.commands.load_helpers.perform_load",
                    new_callable=AsyncMock,
                    return_value=(True, None),
                ):
                    await action_add_preset_or_load_playlist(mock_browser)
        mock_undo.assert_called_once()
