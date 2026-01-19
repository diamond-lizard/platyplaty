#!/usr/bin/env python3
"""Unit tests for autoplay key blocking behavior."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.playlist import Playlist
from platyplaty.playlist_actions import (
    navigate_up, navigate_down, play_next, play_previous,
    reorder_up, reorder_down, delete_from_playlist,
    undo, redo, play_selection, page_up, page_down,
    navigate_to_first_preset, navigate_to_last_preset,
)


@pytest.fixture
def mock_app() -> MagicMock:
    """Create a mock PlatyplatyApp for testing."""
    app = MagicMock()
    app.query_one = MagicMock(return_value=MagicMock())
    return app


@pytest.fixture
def mock_ctx_autoplay_on() -> MagicMock:
    """Create a mock AppContext with autoplay enabled."""
    ctx = MagicMock()
    ctx.current_focus = "playlist"
    ctx.playlist = Playlist([Path("/a.milk"), Path("/b.milk")])
    ctx.autoplay_manager = MagicMock()
    ctx.autoplay_manager.autoplay_enabled = True
    return ctx


class TestAutoplayBlocking:
    """Tests for keys blocked during autoplay."""

    @pytest.mark.asyncio
    async def test_navigate_up_blocked(
        self, mock_ctx_autoplay_on: MagicMock, mock_app: MagicMock
    ) -> None:
        """navigate_up is blocked during autoplay."""
        mock_ctx_autoplay_on.playlist.set_selection(1)
        with patch("platyplaty.playlist_actions.show_autoplay_blocked_error"):
            await navigate_up(mock_ctx_autoplay_on, mock_app)
        assert mock_ctx_autoplay_on.playlist.get_selection() == 1

    @pytest.mark.asyncio
    async def test_navigate_down_blocked(
        self, mock_ctx_autoplay_on: MagicMock, mock_app: MagicMock
    ) -> None:
        """navigate_down is blocked during autoplay."""
        mock_ctx_autoplay_on.playlist.set_selection(0)
        with patch("platyplaty.playlist_actions.show_autoplay_blocked_error"):
            await navigate_down(mock_ctx_autoplay_on, mock_app)
        assert mock_ctx_autoplay_on.playlist.get_selection() == 0

    @pytest.mark.asyncio
    async def test_play_next_blocked(
        self, mock_ctx_autoplay_on: MagicMock, mock_app: MagicMock
    ) -> None:
        """play_next is blocked during autoplay."""
        mock_ctx_autoplay_on.playlist.set_selection(0)
        with patch("platyplaty.playlist_actions.show_autoplay_blocked_error"):
            await play_next(mock_ctx_autoplay_on, mock_app)
        assert mock_ctx_autoplay_on.playlist.get_selection() == 0

    @pytest.mark.asyncio
    async def test_delete_blocked(
        self, mock_ctx_autoplay_on: MagicMock, mock_app: MagicMock
    ) -> None:
        """delete_from_playlist is blocked during autoplay."""
        initial_len = len(mock_ctx_autoplay_on.playlist.presets)
        with patch("platyplaty.playlist_actions.show_autoplay_blocked_error"):
            await delete_from_playlist(mock_ctx_autoplay_on, mock_app)
        assert len(mock_ctx_autoplay_on.playlist.presets) == initial_len

    @pytest.mark.asyncio
    async def test_undo_blocked(
        self, mock_ctx_autoplay_on: MagicMock, mock_app: MagicMock
    ) -> None:
        """undo is blocked during autoplay."""
        with patch("platyplaty.playlist_actions.show_autoplay_blocked_error"):
            await undo(mock_ctx_autoplay_on, mock_app)

    @pytest.mark.asyncio
    async def test_redo_blocked(
        self, mock_ctx_autoplay_on: MagicMock, mock_app: MagicMock
    ) -> None:
        """redo is blocked during autoplay."""
        with patch("platyplaty.playlist_actions.show_autoplay_blocked_error"):
            await redo(mock_ctx_autoplay_on, mock_app)
