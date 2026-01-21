#!/usr/bin/env python3
"""Tests for dirty flag behavior on undo (TASK-36600)."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.playlist import Playlist
from platyplaty.playlist_snapshot import push_undo_snapshot
from platyplaty.playlist_undo_actions import undo, redo
from platyplaty.undo import UndoManager


@pytest.fixture
def mock_app() -> MagicMock:
    """Create a mock PlatyplatyApp for testing."""
    app = MagicMock()
    app.query_one = MagicMock(return_value=MagicMock())
    return app


@pytest.fixture
def mock_ctx() -> MagicMock:
    """Create a mock AppContext with playlist and undo manager."""
    ctx = MagicMock()
    ctx.current_focus = "playlist"
    ctx.playlist = Playlist([
        Path("/test/a.milk"),
        Path("/test/b.milk"),
    ])
    ctx.playlist.set_selection(0)
    ctx.playlist.set_playing(0)
    ctx.playlist.dirty_flag = False
    ctx.undo_manager = UndoManager()
    ctx.autoplay_manager = MagicMock()
    ctx.autoplay_manager.autoplay_enabled = False
    return ctx


class TestUndoDirtyFlag:
    """Tests for dirty flag restoration on undo."""

    @pytest.mark.asyncio
    async def test_undo_restores_dirty_flag_false(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Undo restores dirty_flag to False when it was False."""
        mock_ctx.playlist.dirty_flag = False
        push_undo_snapshot(mock_ctx)
        mock_ctx.playlist.add_preset(Path("/test/c.milk"))
        assert mock_ctx.playlist.dirty_flag is True
        await undo(mock_ctx, mock_app)
        assert mock_ctx.playlist.dirty_flag is False

    @pytest.mark.asyncio
    async def test_undo_restores_dirty_flag_true(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Undo restores dirty_flag to True when it was True."""
        mock_ctx.playlist.dirty_flag = True
        push_undo_snapshot(mock_ctx)
        mock_ctx.playlist.add_preset(Path("/test/c.milk"))
        await undo(mock_ctx, mock_app)
        assert mock_ctx.playlist.dirty_flag is True


class TestRedoDirtyFlag:
    """Tests for dirty flag restoration on redo."""

    @pytest.mark.asyncio
    async def test_redo_restores_dirty_flag_true(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Redo restores dirty_flag to True after undone action."""
        mock_ctx.playlist.dirty_flag = False
        push_undo_snapshot(mock_ctx)
        mock_ctx.playlist.add_preset(Path("/test/c.milk"))
        await undo(mock_ctx, mock_app)
        assert mock_ctx.playlist.dirty_flag is False
        await redo(mock_ctx, mock_app)
        assert mock_ctx.playlist.dirty_flag is True

    @pytest.mark.asyncio
    async def test_redo_preserves_undo_dirty_flag_state(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Redo restores to state captured at time of action."""
        mock_ctx.playlist.dirty_flag = True
        push_undo_snapshot(mock_ctx)
        mock_ctx.playlist.add_preset(Path("/test/c.milk"))
        await undo(mock_ctx, mock_app)
        assert mock_ctx.playlist.dirty_flag is True
        await redo(mock_ctx, mock_app)
        assert mock_ctx.playlist.dirty_flag is True

