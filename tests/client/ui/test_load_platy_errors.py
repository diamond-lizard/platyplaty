#!/usr/bin/env python3
"""Tests for 'a' key error cases when loading .platy files.

This module tests error handling when the 'a' key is pressed on
unreadable .platy files or when the load operation fails.
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


class TestLoadPlatyErrors:
    """Tests for error handling when loading .platy files."""

    @pytest.mark.asyncio
    async def test_unreadable_platy_shows_error(
        self, mock_browser: MagicMock, tmp_path: Path
    ) -> None:
        """'a' on unreadable .platy file shows error message."""
        from platyplaty.ui.file_browser_actions import (
            action_add_preset_or_load_playlist,
        )
        platy_file = tmp_path / "test.platy"
        platy_file.write_text("/preset.milk\n")
        entry = DirectoryEntry("test.platy", EntryType.FILE, platy_file)
        mock_browser.get_selected_entry.return_value = entry
        with patch("platyplaty.ui.file_browser_actions.is_readable", return_value=False):
            with patch("platyplaty.ui.file_browser_actions.show_transient_error") as mock_err:
                await action_add_preset_or_load_playlist(mock_browser)
        mock_err.assert_called_once()
        assert "not readable" in mock_err.call_args[0][1]

    @pytest.mark.asyncio
    async def test_load_failure_shows_error(
        self, mock_browser: MagicMock, tmp_path: Path
    ) -> None:
        """'a' on .platy file shows error when load fails."""
        from platyplaty.ui.file_browser_actions import (
            action_add_preset_or_load_playlist,
        )
        platy_file = tmp_path / "test.platy"
        platy_file.write_text("/preset.milk\n")
        entry = DirectoryEntry("test.platy", EntryType.FILE, platy_file)
        mock_browser.get_selected_entry.return_value = entry
        error_msg = "Error: could not load playlist: parse error"
        with patch("platyplaty.ui.file_browser_actions.is_readable", return_value=True):
            with patch("platyplaty.playlist_snapshot.push_undo_snapshot"):
                with patch(
                    "platyplaty.commands.load_helpers.perform_load",
                    new_callable=AsyncMock,
                    return_value=(False, error_msg),
                ):
                    with patch(
                        "platyplaty.ui.file_browser_actions.show_transient_error"
                    ) as mock_err:
                        await action_add_preset_or_load_playlist(mock_browser)
        mock_err.assert_called_once()
        assert error_msg in mock_err.call_args[0][1]

    @pytest.mark.asyncio
    async def test_no_error_on_success(
        self, mock_browser: MagicMock, tmp_path: Path
    ) -> None:
        """'a' on .platy file does not show error on success."""
        from platyplaty.ui.file_browser_actions import (
            action_add_preset_or_load_playlist,
        )
        platy_file = tmp_path / "test.platy"
        platy_file.write_text("/preset.milk\n")
        entry = DirectoryEntry("test.platy", EntryType.FILE, platy_file)
        mock_browser.get_selected_entry.return_value = entry
        with patch("platyplaty.ui.file_browser_actions.is_readable", return_value=True):
            with patch("platyplaty.playlist_snapshot.push_undo_snapshot"):
                with patch(
                    "platyplaty.commands.load_helpers.perform_load",
                    new_callable=AsyncMock,
                    return_value=(True, None),
                ):
                    with patch(
                        "platyplaty.ui.file_browser_actions.show_transient_error"
                    ) as mock_err:
                        await action_add_preset_or_load_playlist(mock_browser)
        mock_err.assert_not_called()
