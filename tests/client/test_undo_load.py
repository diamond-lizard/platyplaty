#!/usr/bin/env python3
"""Tests for undo/redo of load operation (TASK-36400)."""

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
    ])
    ctx.playlist.set_selection(0)
    ctx.playlist.set_playing(1)
    ctx.undo_manager = UndoManager()
    ctx.autoplay_manager = MagicMock()
    ctx.autoplay_manager.autoplay_enabled = False
    return ctx


class TestUndoLoad:
    """Tests for undo/redo of load operation."""
    
    @pytest.mark.asyncio
    async def test_undo_load_restores_previous_presets(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Undo of load restores previous playlist contents."""
        original_presets = list(mock_ctx.playlist.presets)
        push_undo_snapshot(mock_ctx)
        mock_ctx.playlist.presets = [Path("/new/x.milk"), Path("/new/y.milk")]
        mock_ctx.playlist.set_selection(0)
        await undo(mock_ctx, mock_app)
        assert mock_ctx.playlist.presets == original_presets
    
    @pytest.mark.asyncio
    async def test_undo_load_restores_playing_index(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Undo of load restores the previously playing preset index."""
        original_playing = mock_ctx.playlist.get_playing()
        push_undo_snapshot(mock_ctx)
        mock_ctx.playlist.presets = [Path("/new/x.milk")]
        mock_ctx.playlist.set_playing(0)
        await undo(mock_ctx, mock_app)
        assert mock_ctx.playlist.get_playing() == original_playing
    
    @pytest.mark.asyncio
    async def test_undo_load_restores_filename(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Undo of load restores the associated filename."""
        mock_ctx.playlist.associated_filename = Path("/old.platy")
        push_undo_snapshot(mock_ctx)
        mock_ctx.playlist.presets = [Path("/new/x.milk")]
        mock_ctx.playlist.associated_filename = Path("/new.platy")
        await undo(mock_ctx, mock_app)
        assert mock_ctx.playlist.associated_filename == Path("/old.platy")
