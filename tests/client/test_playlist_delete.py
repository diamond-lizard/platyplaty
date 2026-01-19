#!/usr/bin/env python3
"""Unit tests for playlist deletion (D/DEL keys)."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.playlist import Playlist
from platyplaty.playlist_delete_action import delete_from_playlist


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


class TestDeleteFromPlaylist:
    """Tests for delete_from_playlist (D/DEL key)."""

    @pytest.mark.asyncio
    async def test_delete_removes_selected_preset(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Deletion removes the selected preset from playlist."""
        mock_ctx.playlist.set_selection(1)
        mock_ctx.playlist.set_playing(0)
        await delete_from_playlist(mock_ctx, mock_app)
        assert len(mock_ctx.playlist.presets) == 2
        assert Path("/test/b.milk") not in mock_ctx.playlist.presets

    @pytest.mark.asyncio
    async def test_delete_selection_moves_to_next(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """After deletion, selection moves to next item."""
        mock_ctx.playlist.set_selection(0)
        mock_ctx.playlist.set_playing(2)
        await delete_from_playlist(mock_ctx, mock_app)
        assert mock_ctx.playlist.get_selection() == 0
        assert mock_ctx.playlist.presets[0] == Path("/test/b.milk")

    @pytest.mark.asyncio
    async def test_delete_at_end_moves_to_last(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Deletion at end moves selection to new last item."""
        mock_ctx.playlist.set_selection(2)
        mock_ctx.playlist.set_playing(0)
        await delete_from_playlist(mock_ctx, mock_app)
        assert mock_ctx.playlist.get_selection() == 1
        assert len(mock_ctx.playlist.presets) == 2

    @pytest.mark.asyncio
    async def test_delete_playing_starts_next(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Deleting the playing preset starts playing the next."""
        mock_ctx.playlist.set_selection(1)
        mock_ctx.playlist.set_playing(1)
        with patch("platyplaty.playlist_actions._load_preset_at_index", new_callable=AsyncMock):
            await delete_from_playlist(mock_ctx, mock_app)
        assert mock_ctx.playlist.get_playing() == 1
        assert mock_ctx.playlist.presets[1] == Path("/test/c.milk")

    @pytest.mark.asyncio
    async def test_delete_last_item_empties_playlist(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Deleting last remaining item leaves empty playlist."""
        mock_ctx.playlist = Playlist([Path("/test/a.milk")])
        mock_ctx.playlist.set_selection(0)
        mock_ctx.playlist.set_playing(0)
        await delete_from_playlist(mock_ctx, mock_app)
        assert len(mock_ctx.playlist.presets) == 0
        assert mock_ctx.playlist.get_playing() is None
