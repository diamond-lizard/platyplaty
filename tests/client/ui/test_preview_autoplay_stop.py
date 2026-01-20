#!/usr/bin/env python3
"""Tests for autoplay stopping on preset preview.

This module tests that ENTER preview and J/K play actions stop autoplay.
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


class TestPreviewStopsAutoplay:
    """Tests for ENTER preview stopping autoplay."""

    @pytest.mark.asyncio
    async def test_enter_preview_stops_autoplay(
        self, mock_browser: MagicMock, tmp_path: Path
    ) -> None:
        """ENTER preview calls stop_autoplay on autoplay_manager."""
        from platyplaty.ui.file_browser_preset_preview import action_preview_preset
        milk_file = tmp_path / "test.milk"
        milk_file.write_text("content")
        entry = DirectoryEntry("test.milk", EntryType.FILE, milk_file)
        mock_browser.get_selected_entry.return_value = entry
        with patch("platyplaty.autoplay_helpers.try_load_preset") as mock_load:
            mock_load.return_value = (True, None)
            with patch("platyplaty.ui.file_browser_preset_preview._update_playing_indicator"):
                await action_preview_preset(mock_browser)
        mock_browser.app.ctx.autoplay_manager.stop_autoplay.assert_called_once()


class TestJKStopsAutoplay:
    """Tests for J/K play stopping autoplay."""

    @pytest.mark.asyncio
    async def test_play_next_stops_autoplay(self, mock_browser: MagicMock) -> None:
        """J (play next) stops autoplay."""
        from platyplaty.ui.file_browser_play_actions import action_play_next_preset
        entries = [
            DirectoryEntry("a.milk", EntryType.FILE, Path("/a.milk")),
            DirectoryEntry("b.milk", EntryType.FILE, Path("/b.milk")),
        ]
        mock_browser.selected_index = 0
        mock_browser._middle_listing = make_listing(entries)
        mock_browser._nav_state = MagicMock()
        mock_browser._nav_state.scroll_offset = 0
        mock_browser.size = MagicMock()
        mock_browser.size.height = 20
        mock_browser.get_selected_entry.return_value = entries[1]
        with patch("platyplaty.ui.file_browser_preset_preview._stop_autoplay_if_running") as mock_stop:
            with patch("platyplaty.autoplay_helpers.try_load_preset") as mock_load:
                mock_load.return_value = (True, None)
                with patch("platyplaty.ui.file_browser_preset_preview._update_playing_indicator"):
                    await action_play_next_preset(mock_browser)
        mock_stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_play_previous_stops_autoplay(self, mock_browser: MagicMock) -> None:
        """K (play previous) stops autoplay."""
        from platyplaty.ui.file_browser_play_actions import action_play_previous_preset
        entries = [
            DirectoryEntry("a.milk", EntryType.FILE, Path("/a.milk")),
            DirectoryEntry("b.milk", EntryType.FILE, Path("/b.milk")),
        ]
        mock_browser.selected_index = 1
        mock_browser._middle_listing = make_listing(entries)
        mock_browser._nav_state = MagicMock()
        mock_browser._nav_state.scroll_offset = 0
        mock_browser.size = MagicMock()
        mock_browser.size.height = 20
        mock_browser.get_selected_entry.return_value = entries[0]
        with patch("platyplaty.ui.file_browser_preset_preview._stop_autoplay_if_running") as mock_stop:
            with patch("platyplaty.autoplay_helpers.try_load_preset") as mock_load:
                mock_load.return_value = (True, None)
                with patch("platyplaty.ui.file_browser_preset_preview._update_playing_indicator"):
                    await action_play_previous_preset(mock_browser)
        mock_stop.assert_called_once()
