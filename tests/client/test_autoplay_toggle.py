#!/usr/bin/env python3
"""Unit tests for AutoplayManager toggle behavior."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.autoplay_manager import AutoplayManager
from platyplaty.playlist import Playlist


@pytest.fixture
def mock_context() -> MagicMock:
    """Create a mock application context."""
    ctx = MagicMock()
    ctx.playlist = Playlist([Path("/test/a.milk"), Path("/test/b.milk")])
    ctx.client = AsyncMock()
    ctx.client.send_command = AsyncMock()
    return ctx


@pytest.fixture
def mock_app() -> MagicMock:
    """Create a mock Textual application."""
    app = MagicMock()
    app.query_one = MagicMock(return_value=MagicMock())
    return app


class TestAutoplayToggle:
    """Tests for autoplay toggle behavior."""

    def test_initial_state_is_off(
        self, mock_context: MagicMock, mock_app: MagicMock
    ) -> None:
        """AutoplayManager starts with autoplay disabled."""
        manager = AutoplayManager(mock_context, mock_app, preset_duration=30.0)
        assert manager.autoplay_enabled is False

    @pytest.mark.asyncio
    async def test_toggle_on_returns_true(
        self, mock_context: MagicMock, mock_app: MagicMock
    ) -> None:
        """toggle_autoplay returns True when turning on."""
        mock_context.playlist.set_playing(0)
        manager = AutoplayManager(mock_context, mock_app, preset_duration=30.0)
        result = await manager.toggle_autoplay()
        assert result is True
        assert manager.autoplay_enabled is True

    @pytest.mark.asyncio
    async def test_toggle_off_returns_false(
        self, mock_context: MagicMock, mock_app: MagicMock
    ) -> None:
        """toggle_autoplay returns False when turning off."""
        mock_context.playlist.set_playing(0)
        manager = AutoplayManager(mock_context, mock_app, preset_duration=30.0)
        await manager.toggle_autoplay()  # Turn on
        result = await manager.toggle_autoplay()  # Turn off
        assert result is False
        assert manager.autoplay_enabled is False
