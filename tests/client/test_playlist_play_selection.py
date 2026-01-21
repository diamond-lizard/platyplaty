#!/usr/bin/env python3
"""Unit tests for playlist play_selection (ENTER key)."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.playlist import Playlist
from platyplaty.playlist_play_actions import play_selection


@pytest.fixture
def mock_app() -> MagicMock:
    """Create a mock PlatyplatyApp for testing."""
    app = MagicMock()
    app.query_one = MagicMock(return_value=MagicMock())
    return app


@pytest.fixture
def mock_ctx() -> MagicMock:
    """Create a mock AppContext with playlist."""
    ctx = MagicMock()
    ctx.current_focus = "playlist"
    ctx.playlist = Playlist([
        Path("/test/a.milk"),
        Path("/test/b.milk"),
        Path("/test/c.milk"),
    ])
    ctx.autoplay_manager = MagicMock()
    ctx.autoplay_manager.autoplay_enabled = False
    return ctx


class TestPlaySelection:
    """Tests for play_selection (ENTER key)."""

    @pytest.mark.asyncio
    async def test_play_selection_moves_playing_to_selection(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """play_selection moves playing indicator to current selection."""
        mock_ctx.playlist.set_selection(2)
        mock_ctx.playlist.set_playing(0)
        with patch(
            "platyplaty.autoplay_helpers.try_load_preset",
            new_callable=AsyncMock
        ):
            await play_selection(mock_ctx, mock_app)
        assert mock_ctx.playlist.get_playing() == 2

    @pytest.mark.asyncio
    async def test_play_selection_loads_selected_preset(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """play_selection loads the currently selected preset."""
        mock_ctx.playlist.set_selection(1)
        mock_load = AsyncMock()
        with patch("platyplaty.autoplay_helpers.try_load_preset", mock_load):
            await play_selection(mock_ctx, mock_app)
        mock_load.assert_called_once_with(mock_ctx, Path("/test/b.milk"))

    @pytest.mark.asyncio
    async def test_play_selection_on_empty_playlist_is_noop(
        self, mock_app: MagicMock
    ) -> None:
        """play_selection on empty playlist does nothing."""
        ctx = MagicMock()
        ctx.current_focus = "playlist"
        ctx.playlist = Playlist([])
        ctx.autoplay_manager = MagicMock()
        ctx.autoplay_manager.autoplay_enabled = False
        mock_load = AsyncMock()
        with patch("platyplaty.autoplay_helpers.try_load_preset", mock_load):
            await play_selection(ctx, mock_app)
        mock_load.assert_not_called()

    @pytest.mark.asyncio
    async def test_play_selection_blocked_during_autoplay(
        self, mock_app: MagicMock
    ) -> None:
        """play_selection is blocked when autoplay is enabled."""
        ctx = MagicMock()
        ctx.current_focus = "playlist"
        ctx.playlist = Playlist([Path("/a.milk")])
        ctx.autoplay_manager = MagicMock()
        ctx.autoplay_manager.autoplay_enabled = True
        ctx.playlist.set_playing(0)
        mock_load = AsyncMock()
        with (
            patch("platyplaty.autoplay_helpers.try_load_preset", mock_load),
            patch("platyplaty.ui.playlist_key.show_autoplay_blocked_error"),
        ):
            await play_selection(ctx, mock_app)
        mock_load.assert_not_called()
