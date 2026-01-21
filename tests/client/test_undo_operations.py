#!/usr/bin/env python3
"""Tests for undo/redo of each operation type (TASK-36400)."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.playlist import Playlist
from platyplaty.playlist_snapshot import push_undo_snapshot
from platyplaty.playlist_undo_actions import redo, undo
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
        Path("/test/c.milk"),
    ])
    ctx.playlist.set_selection(0)
    ctx.playlist.set_playing(1)
    ctx.undo_manager = UndoManager()
    ctx.autoplay_manager = MagicMock()
    ctx.autoplay_manager.autoplay_enabled = False
    return ctx


class TestUndoAdd:
    """Tests for undo/redo of add operation."""
    
    @pytest.mark.asyncio
    async def test_undo_add_removes_preset(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Undo of add removes the added preset."""
        push_undo_snapshot(mock_ctx)
        mock_ctx.playlist.add_preset(Path("/test/d.milk"))
        assert len(mock_ctx.playlist.presets) == 4
        await undo(mock_ctx, mock_app)
        assert len(mock_ctx.playlist.presets) == 3
    
    @pytest.mark.asyncio
    async def test_redo_add_restores_preset(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Redo of add restores the added preset."""
        push_undo_snapshot(mock_ctx)
        mock_ctx.playlist.add_preset(Path("/test/d.milk"))
        await undo(mock_ctx, mock_app)
        await redo(mock_ctx, mock_app)
        assert len(mock_ctx.playlist.presets) == 4


class TestUndoDelete:
    """Tests for undo/redo of delete operation."""
    
    @pytest.mark.asyncio
    async def test_undo_delete_restores_preset(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Undo of delete restores the deleted preset."""
        push_undo_snapshot(mock_ctx)
        mock_ctx.playlist.remove_preset(1)
        assert len(mock_ctx.playlist.presets) == 2
        await undo(mock_ctx, mock_app)
        assert len(mock_ctx.playlist.presets) == 3
    
    @pytest.mark.asyncio
    async def test_undo_delete_restores_position(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Undo of delete restores preset to original position."""
        original = mock_ctx.playlist.presets[1]
        push_undo_snapshot(mock_ctx)
        mock_ctx.playlist.remove_preset(1)
        await undo(mock_ctx, mock_app)
        assert mock_ctx.playlist.presets[1] == original
