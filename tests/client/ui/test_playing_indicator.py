#!/usr/bin/env python3
"""Tests for playing indicator ('* ') movement on preview.

This module tests that the playing indicator moves correctly when
previewing presets from the file browser.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))


@pytest.fixture
def mock_browser() -> MagicMock:
    """Create a mock FileBrowser for testing."""
    browser = MagicMock()
    browser.app = MagicMock()
    browser.app.ctx = MagicMock()
    browser.app.ctx.playlist = MagicMock()
    browser.app.ctx.playlist.presets = []
    browser.app.ctx.autoplay_manager = MagicMock()
    return browser


class TestIndicatorMovesToPlaylist:
    """Tests for indicator moving when preset is in playlist."""

    @pytest.mark.asyncio
    async def test_indicator_moves_to_preset_in_playlist(
        self, mock_browser: MagicMock, tmp_path: Path
    ) -> None:
        """Indicator moves to preset when it is in playlist."""
        from platyplaty.ui.file_browser_preset_preview import _update_playing_indicator
        preset_path = tmp_path / "test.milk"
        mock_browser.app.ctx.playlist.presets = [preset_path]
        with patch("platyplaty.playlist_action_helpers.find_preset_index") as mock_find:
            mock_find.return_value = 0
            with patch("platyplaty.playlist_action_helpers.refresh_playlist_view"):
                with patch("platyplaty.playlist_action_helpers.scroll_playlist_to_playing"):
                    _update_playing_indicator(mock_browser, preset_path)
        mock_browser.app.ctx.playlist.set_playing.assert_called_once_with(0)


class TestIndicatorRemovedIfNotInPlaylist:
    """Tests for indicator removal when preset not in playlist."""

    @pytest.mark.asyncio
    async def test_indicator_removed_if_not_in_playlist(
        self, mock_browser: MagicMock, tmp_path: Path
    ) -> None:
        """Indicator is removed when preset is not in playlist."""
        from platyplaty.ui.file_browser_preset_preview import _update_playing_indicator
        preset_path = tmp_path / "preview.milk"
        mock_browser.app.ctx.playlist.presets = []
        with patch("platyplaty.playlist_action_helpers.find_preset_index") as mock_find:
            mock_find.return_value = None
            with patch("platyplaty.playlist_action_helpers.refresh_playlist_view"):
                _update_playing_indicator(mock_browser, preset_path)
        mock_browser.app.ctx.playlist.set_playing.assert_called_once_with(None)


class TestScrollToPlayingIndicator:
    """Tests for scrolling playlist to make indicator visible."""

    @pytest.mark.asyncio
    async def test_scrolls_when_preset_in_playlist(
        self, mock_browser: MagicMock, tmp_path: Path
    ) -> None:
        """Playlist scrolls to make playing indicator visible."""
        from platyplaty.ui.file_browser_preset_preview import _update_playing_indicator
        preset_path = tmp_path / "test.milk"
        mock_browser.app.ctx.playlist.presets = [preset_path]
        with patch("platyplaty.playlist_action_helpers.find_preset_index") as mock_find:
            mock_find.return_value = 5
            with patch("platyplaty.playlist_action_helpers.refresh_playlist_view"):
                with patch("platyplaty.playlist_action_helpers.scroll_playlist_to_playing") as mock_scroll:
                    _update_playing_indicator(mock_browser, preset_path)
        mock_scroll.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_scroll_when_not_in_playlist(
        self, mock_browser: MagicMock, tmp_path: Path
    ) -> None:
        """No scroll when preset is not in playlist."""
        from platyplaty.ui.file_browser_preset_preview import _update_playing_indicator
        preset_path = tmp_path / "preview.milk"
        with patch("platyplaty.playlist_action_helpers.find_preset_index") as mock_find:
            mock_find.return_value = None
            with patch("platyplaty.playlist_action_helpers.refresh_playlist_view"):
                with patch("platyplaty.playlist_action_helpers.scroll_playlist_to_playing") as mock_scroll:
                    _update_playing_indicator(mock_browser, preset_path)
        mock_scroll.assert_not_called()
