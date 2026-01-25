#!/usr/bin/env python3
"""Tests for ENTER key preset preview behavior in file browser.

This module tests the action_preview_preset function which handles
the ENTER key to preview presets without adding them to the playlist.
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
    browser.app = MagicMock()
    browser.app.ctx = MagicMock()
    browser.app.ctx.playlist = MagicMock()
    browser.app.ctx.autoplay_manager = MagicMock()
    return browser


class TestPreviewMilkFile:
    """Tests for previewing .milk files."""

    @pytest.mark.asyncio
    async def test_milk_file_loads_into_renderer(
        self, mock_browser: MagicMock, tmp_path: Path
    ) -> None:
        """ENTER on .milk file loads it into renderer."""
        from platyplaty.ui.file_browser_preset_preview import action_preview_preset
        milk_file = tmp_path / "test.milk"
        milk_file.write_text("content")
        entry = DirectoryEntry("test.milk", EntryType.FILE, milk_file)
        mock_browser.get_selected_entry.return_value = entry
        with patch("platyplaty.preset_command.load_preset") as mock_load:
            mock_load.return_value = (True, None)
            with patch("platyplaty.ui.file_browser_preset_preview._update_playing_indicator"):
                await action_preview_preset(mock_browser)
        mock_load.assert_called_once()
        assert mock_load.call_args[0][1] == milk_file

    @pytest.mark.asyncio
    async def test_symlink_to_milk_loads(
        self, mock_browser: MagicMock, tmp_path: Path
    ) -> None:
        """ENTER on symlink to .milk file loads into renderer."""
        from platyplaty.ui.file_browser_preset_preview import action_preview_preset
        target = tmp_path / "target.milk"
        target.write_text("content")
        symlink = tmp_path / "link.milk"
        symlink.symlink_to(target)
        entry = DirectoryEntry("link.milk", EntryType.SYMLINK_TO_FILE, symlink)
        mock_browser.get_selected_entry.return_value = entry
        with patch("platyplaty.preset_command.load_preset") as mock_load:
            mock_load.return_value = (True, None)
            with patch("platyplaty.ui.file_browser_preset_preview._update_playing_indicator"):
                await action_preview_preset(mock_browser)
        mock_load.assert_called_once()
        assert mock_load.call_args[0][1] == symlink
