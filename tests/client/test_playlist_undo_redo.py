#!/usr/bin/env python3
"""Unit tests for playlist undo/redo (u/Ctrl+r keys)."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.playlist import Playlist
from platyplaty.undo import UndoManager
from platyplaty.playlist_snapshot import create_snapshot, push_undo_snapshot
from platyplaty.playlist_actions import undo, redo


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
    ctx.undo_manager = UndoManager(max_undo=10)
    ctx.autoplay_manager = MagicMock()
    ctx.autoplay_manager.autoplay_enabled = False
    return ctx


class TestUndo:
    """Tests for undo (u key)."""

    @pytest.mark.asyncio
    async def test_undo_restores_previous_state(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Undo restores the previous playlist state."""
        push_undo_snapshot(mock_ctx)
        mock_ctx.playlist.add_preset(Path("/test/c.milk"))
        await undo(mock_ctx, mock_app)
        assert len(mock_ctx.playlist.presets) == 2

    @pytest.mark.asyncio
    async def test_undo_empty_stack_shows_error(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Undo with empty stack shows error message."""
        await undo(mock_ctx, mock_app)


class TestRedo:
    """Tests for redo (Ctrl+r key)."""

    @pytest.mark.asyncio
    async def test_redo_restores_next_state(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Redo restores the next state after undo."""
        push_undo_snapshot(mock_ctx)
        mock_ctx.playlist.add_preset(Path("/test/c.milk"))
        await undo(mock_ctx, mock_app)
        await redo(mock_ctx, mock_app)
        assert len(mock_ctx.playlist.presets) == 3

    @pytest.mark.asyncio
    async def test_redo_empty_stack_shows_error(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Redo with empty stack shows error message."""
        await redo(mock_ctx, mock_app)
