#!/usr/bin/env python3
"""Unit tests for shuffle behavior during autoplay."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestShuffleDuringAutoplay:
    """Tests for shuffle not resetting autoplay timer."""

    @pytest.fixture
    def mock_playlist(self):
        """Create a mock Playlist with presets."""
        playlist = MagicMock()
        playlist.presets = [
            Path("/a.milk"),
            Path("/b.milk"),
            Path("/c.milk"),
        ]
        playlist.get_selection.return_value = 1
        playlist.get_playing.return_value = 1  # /b.milk playing
        return playlist

    @pytest.fixture
    def mock_ctx(self, mock_playlist):
        """Create a mock AppContext."""
        ctx = MagicMock()
        ctx.playlist = mock_playlist
        ctx.autoplay_manager = MagicMock()
        return ctx

    @pytest.mark.asyncio
    async def test_shuffle_does_not_reset_timer(self, mock_ctx):
        """Shuffle does not call reset_timer on autoplay manager."""
        from platyplaty.commands.shuffle_playlist import execute

        with patch("platyplaty.commands.shuffle_playlist.push_undo_snapshot"):
            await execute(mock_ctx)

        # Verify reset_timer was NOT called
        mock_ctx.autoplay_manager.reset_timer.assert_not_called()

    @pytest.mark.asyncio
    async def test_shuffle_does_not_stop_autoplay(self, mock_ctx):
        """Shuffle does not stop autoplay."""
        from platyplaty.commands.shuffle_playlist import execute

        with patch("platyplaty.commands.shuffle_playlist.push_undo_snapshot"):
            await execute(mock_ctx)

        # Verify stop_autoplay was NOT called
        mock_ctx.autoplay_manager.stop_autoplay.assert_not_called()
