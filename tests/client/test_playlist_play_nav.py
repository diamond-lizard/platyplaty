#!/usr/bin/env python3
"""Unit tests for playlist play next/previous (J/K keys)."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.playlist import Playlist
from platyplaty.playlist_play_actions import play_next, play_previous


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


class TestPlayNext:
    """Tests for play_next (J key)."""

    @pytest.mark.asyncio
    async def test_play_next_moves_selection_and_playing(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """play_next moves both selection and playing indicator."""
        mock_ctx.playlist.set_selection(0)
        mock_ctx.playlist.set_playing(0)
        with patch("platyplaty.preset_command.load_preset", new_callable=AsyncMock):
            await play_next(mock_ctx, mock_app)
        assert mock_ctx.playlist.get_selection() == 1
        assert mock_ctx.playlist.get_playing() == 1

    @pytest.mark.asyncio
    async def test_play_next_at_last_is_noop(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """play_next at last item does not change anything."""
        mock_ctx.playlist.set_selection(2)
        mock_ctx.playlist.set_playing(2)
        with patch("platyplaty.preset_command.load_preset", new_callable=AsyncMock):
            await play_next(mock_ctx, mock_app)
        assert mock_ctx.playlist.get_selection() == 2
        assert mock_ctx.playlist.get_playing() == 2


class TestPlayPrevious:
    """Tests for play_previous (K key)."""

    @pytest.mark.asyncio
    async def test_play_previous_moves_selection_and_playing(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """play_previous moves both selection and playing indicator."""
        mock_ctx.playlist.set_selection(1)
        mock_ctx.playlist.set_playing(1)
        with patch("platyplaty.preset_command.load_preset", new_callable=AsyncMock):
            await play_previous(mock_ctx, mock_app)
        assert mock_ctx.playlist.get_selection() == 0
        assert mock_ctx.playlist.get_playing() == 0

    @pytest.mark.asyncio
    async def test_play_previous_at_first_is_noop(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """play_previous at first item does not change anything."""
        mock_ctx.playlist.set_selection(0)
        mock_ctx.playlist.set_playing(0)
        with patch("platyplaty.preset_command.load_preset", new_callable=AsyncMock):
            await play_previous(mock_ctx, mock_app)
        assert mock_ctx.playlist.get_selection() == 0
        assert mock_ctx.playlist.get_playing() == 0
