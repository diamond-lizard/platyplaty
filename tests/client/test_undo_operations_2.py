#!/usr/bin/env python3
"""Tests for undo/redo of reorder, shuffle, load, clear (TASK-36400)."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.playlist import Playlist
from platyplaty.playlist_snapshot import push_undo_snapshot
from platyplaty.playlist_undo_actions import undo
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


class TestUndoReorder:
    """Tests for undo/redo of reorder operation."""
    
    @pytest.mark.asyncio
    async def test_undo_reorder_up_restores_order(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Undo of reorder up restores original order."""
        original_order = list(mock_ctx.playlist.presets)
        push_undo_snapshot(mock_ctx)
        mock_ctx.playlist.move_preset_up(1)
        await undo(mock_ctx, mock_app)
        assert mock_ctx.playlist.presets == original_order
    
    @pytest.mark.asyncio
    async def test_undo_reorder_down_restores_order(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Undo of reorder down restores original order."""
        original_order = list(mock_ctx.playlist.presets)
        push_undo_snapshot(mock_ctx)
        mock_ctx.playlist.move_preset_down(0)
        await undo(mock_ctx, mock_app)
        assert mock_ctx.playlist.presets == original_order


class TestUndoShuffle:
    """Tests for undo/redo of shuffle operation."""
    
    @pytest.mark.asyncio
    async def test_undo_shuffle_restores_order(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Undo of shuffle restores original order."""
        import random
        original_order = list(mock_ctx.playlist.presets)
        push_undo_snapshot(mock_ctx)
        random.shuffle(mock_ctx.playlist.presets)
        await undo(mock_ctx, mock_app)
        assert mock_ctx.playlist.presets == original_order


class TestUndoLoadClear:
    """Tests for undo/redo of load and clear operations."""
    
    @pytest.mark.asyncio
    async def test_undo_clear_restores_presets(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Undo of clear restores the cleared presets."""
        push_undo_snapshot(mock_ctx)
        mock_ctx.playlist.clear()
        assert len(mock_ctx.playlist.presets) == 0
        await undo(mock_ctx, mock_app)
        assert len(mock_ctx.playlist.presets) == 3
