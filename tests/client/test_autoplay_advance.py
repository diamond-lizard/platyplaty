#!/usr/bin/env python3
"""Unit tests for AutoplayManager timer advancement."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.autoplay_manager import AutoplayManager
from platyplaty.playlist import Playlist


@pytest.fixture
def mock_context() -> MagicMock:
    """Create a mock application context with playable presets."""
    ctx = MagicMock()
    ctx.playlist = Playlist([Path("/test/a.milk"), Path("/test/b.milk")])
    ctx.client = AsyncMock()
    ctx.client.send_command = AsyncMock()
    ctx.renderer_process = MagicMock()
    ctx.renderer_process.returncode = None
    return ctx


@pytest.fixture
def mock_app() -> MagicMock:
    """Create a mock Textual application."""
    app = MagicMock()
    app.query_one = MagicMock(return_value=MagicMock())
    return app


class TestAdvanceToNext:
    """Tests for advance_to_next() method."""

    @pytest.mark.asyncio
    async def test_advance_from_first_to_second(
        self, mock_context: MagicMock, mock_app: MagicMock, tmp_path: Path
    ) -> None:
        """advance_to_next moves from first to second preset."""
        # Create real files so is_preset_playable returns True
        a_milk = tmp_path / "a.milk"
        b_milk = tmp_path / "b.milk"
        a_milk.touch()
        b_milk.touch()
        mock_context.playlist = Playlist([a_milk, b_milk])
        mock_context.playlist.set_playing(0)
        manager = AutoplayManager(mock_context, mock_app, preset_duration=30.0)
        result = await manager.advance_to_next()
        assert result is True
        assert mock_context.playlist.get_playing() == 1

    @pytest.mark.asyncio
    async def test_advance_updates_selection(
        self, mock_context: MagicMock, mock_app: MagicMock, tmp_path: Path
    ) -> None:
        """advance_to_next also updates selection index."""
        a_milk = tmp_path / "a.milk"
        b_milk = tmp_path / "b.milk"
        a_milk.touch()
        b_milk.touch()
        mock_context.playlist = Playlist([a_milk, b_milk])
        mock_context.playlist.set_playing(0)
        mock_context.playlist.set_selection(0)
        manager = AutoplayManager(mock_context, mock_app, preset_duration=30.0)
        await manager.advance_to_next()
        assert mock_context.playlist.get_selection() == 1

    @pytest.mark.asyncio
    async def test_advance_sends_load_command(
        self, mock_context: MagicMock, mock_app: MagicMock, tmp_path: Path
    ) -> None:
        """advance_to_next sends LOAD PRESET command to renderer."""
        a_milk = tmp_path / "a.milk"
        b_milk = tmp_path / "b.milk"
        a_milk.touch()
        b_milk.touch()
        mock_context.playlist = Playlist([a_milk, b_milk])
        mock_context.playlist.set_playing(0)
        manager = AutoplayManager(mock_context, mock_app, preset_duration=30.0)
        await manager.advance_to_next()
        mock_context.client.send_command.assert_called_once()
