#!/usr/bin/env python3
"""Unit tests for playlist selection navigation (j/k keys)."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.playlist import Playlist
from platyplaty.playlist_actions import navigate_up, navigate_down


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


class TestNavigateDown:
    """Tests for navigate_down (j key)."""

    @pytest.mark.asyncio
    async def test_navigate_down_moves_selection(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """navigate_down moves selection from 0 to 1."""
        mock_ctx.playlist.set_selection(0)
        await navigate_down(mock_ctx, mock_app)
        assert mock_ctx.playlist.get_selection() == 1

    @pytest.mark.asyncio
    async def test_navigate_down_at_last_is_noop(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """navigate_down at last item does not change selection."""
        mock_ctx.playlist.set_selection(2)
        await navigate_down(mock_ctx, mock_app)
        assert mock_ctx.playlist.get_selection() == 2

    @pytest.mark.asyncio
    async def test_navigate_down_does_not_change_playing(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """navigate_down does not affect playing index."""
        mock_ctx.playlist.set_selection(0)
        mock_ctx.playlist.set_playing(0)
        await navigate_down(mock_ctx, mock_app)
        assert mock_ctx.playlist.get_playing() == 0


class TestNavigateUp:
    """Tests for navigate_up (k key)."""

    @pytest.mark.asyncio
    async def test_navigate_up_moves_selection(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """navigate_up moves selection from 1 to 0."""
        mock_ctx.playlist.set_selection(1)
        await navigate_up(mock_ctx, mock_app)
        assert mock_ctx.playlist.get_selection() == 0

    @pytest.mark.asyncio
    async def test_navigate_up_at_first_is_noop(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """navigate_up at first item does not change selection."""
        mock_ctx.playlist.set_selection(0)
        await navigate_up(mock_ctx, mock_app)
        assert mock_ctx.playlist.get_selection() == 0

    @pytest.mark.asyncio
    async def test_navigate_up_does_not_change_playing(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """navigate_up does not affect playing index."""
        mock_ctx.playlist.set_selection(1)
        mock_ctx.playlist.set_playing(1)
        await navigate_up(mock_ctx, mock_app)
        assert mock_ctx.playlist.get_playing() == 1
