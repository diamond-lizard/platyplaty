#!/usr/bin/env python3
"""Tests for ENTER key no-op cases in file browser.

This module tests cases where ENTER does nothing: directories,
.platy files, and broken symlinks.
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
    browser.app.ctx.autoplay_manager = MagicMock()
    return browser


class TestPreviewNoOp:
    """Tests for ENTER on non-previewable entries (no-ops)."""

    @pytest.mark.asyncio
    async def test_directory_is_noop(self, mock_browser: MagicMock) -> None:
        """ENTER on directory does nothing."""
        from platyplaty.ui.file_browser_preset_preview import action_preview_preset
        entry = DirectoryEntry("subdir", EntryType.DIRECTORY, Path("/subdir"))
        mock_browser.get_selected_entry.return_value = entry
        with patch("platyplaty.ui.file_browser_preset_preview.try_load_preset") as mock_load:
            await action_preview_preset(mock_browser)
        mock_load.assert_not_called()

    @pytest.mark.asyncio
    async def test_symlink_to_dir_is_noop(self, mock_browser: MagicMock) -> None:
        """ENTER on symlink to directory does nothing."""
        from platyplaty.ui.file_browser_preset_preview import action_preview_preset
        entry = DirectoryEntry("link", EntryType.SYMLINK_TO_DIRECTORY, Path("/link"))
        mock_browser.get_selected_entry.return_value = entry
        with patch("platyplaty.ui.file_browser_preset_preview.try_load_preset") as mock_load:
            await action_preview_preset(mock_browser)
        mock_load.assert_not_called()

    @pytest.mark.asyncio
    async def test_platy_file_is_noop(self, mock_browser: MagicMock) -> None:
        """ENTER on .platy file does nothing."""
        from platyplaty.ui.file_browser_preset_preview import action_preview_preset
        entry = DirectoryEntry("playlist.platy", EntryType.FILE, Path("/playlist.platy"))
        mock_browser.get_selected_entry.return_value = entry
        with patch("platyplaty.ui.file_browser_preset_preview.try_load_preset") as mock_load:
            await action_preview_preset(mock_browser)
        mock_load.assert_not_called()

    @pytest.mark.asyncio
    async def test_broken_symlink_is_noop(self, mock_browser: MagicMock) -> None:
        """ENTER on broken symlink does nothing."""
        from platyplaty.ui.file_browser_preset_preview import action_preview_preset
        entry = DirectoryEntry("broken.milk", EntryType.BROKEN_SYMLINK, Path("/broken"))
        mock_browser.get_selected_entry.return_value = entry
        with patch("platyplaty.ui.file_browser_preset_preview.try_load_preset") as mock_load:
            await action_preview_preset(mock_browser)
        mock_load.assert_not_called()
