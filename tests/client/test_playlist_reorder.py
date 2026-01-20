#!/usr/bin/env python3
"""Unit tests for playlist reordering (Ctrl+j/k keys)."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.playlist import Playlist
from platyplaty.playlist_reorder_actions import reorder_up, reorder_down


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


class TestReorderUp:
    """Tests for reorder_up (Ctrl+k key)."""

    @pytest.mark.asyncio
    async def test_reorder_up_moves_preset(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """reorder_up swaps preset with the one above."""
        mock_ctx.playlist.set_selection(1)
        await reorder_up(mock_ctx, mock_app)
        assert mock_ctx.playlist.presets[0] == Path("/test/b.milk")
        assert mock_ctx.playlist.presets[1] == Path("/test/a.milk")
        assert mock_ctx.playlist.get_selection() == 0

    @pytest.mark.asyncio
    async def test_reorder_up_at_first_is_noop(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """reorder_up at first position does nothing."""
        mock_ctx.playlist.set_selection(0)
        await reorder_up(mock_ctx, mock_app)
        assert mock_ctx.playlist.presets[0] == Path("/test/a.milk")
        assert mock_ctx.playlist.get_selection() == 0


class TestReorderDown:
    """Tests for reorder_down (Ctrl+j key)."""

    @pytest.mark.asyncio
    async def test_reorder_down_moves_preset(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """reorder_down swaps preset with the one below."""
        mock_ctx.playlist.set_selection(1)
        await reorder_down(mock_ctx, mock_app)
        assert mock_ctx.playlist.presets[1] == Path("/test/c.milk")
        assert mock_ctx.playlist.presets[2] == Path("/test/b.milk")
        assert mock_ctx.playlist.get_selection() == 2

    @pytest.mark.asyncio
    async def test_reorder_down_at_last_is_noop(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """reorder_down at last position does nothing."""
        mock_ctx.playlist.set_selection(2)
        await reorder_down(mock_ctx, mock_app)
        assert mock_ctx.playlist.presets[2] == Path("/test/c.milk")
        assert mock_ctx.playlist.get_selection() == 2
