#!/usr/bin/env python3
"""Unit tests for :shuffle command preserving selection and playing state."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestShufflePreservesSelection:
    """Tests for shuffle preserving selection."""

    @pytest.fixture
    def mock_playlist(self):
        """Create a mock Playlist with presets."""
        playlist = MagicMock()
        playlist.presets = [
            Path("/a.milk"),
            Path("/b.milk"),
            Path("/c.milk"),
        ]
        playlist.get_selection.return_value = 1  # /b.milk selected
        playlist.get_playing.return_value = None
        return playlist

    @pytest.fixture
    def mock_ctx(self, mock_playlist):
        """Create a mock AppContext."""
        ctx = MagicMock()
        ctx.playlist = mock_playlist
        return ctx

    @pytest.mark.asyncio
    async def test_shuffle_preserves_selected_preset(
        self, mock_ctx, mock_playlist
    ):
        """Shuffle keeps the same preset selected."""
        from platyplaty.commands.shuffle_playlist import execute

        # After shuffle, presets list is reordered
        def reorder_presets():
            mock_playlist.presets = [
                Path("/c.milk"),
                Path("/a.milk"),
                Path("/b.milk"),
            ]

        mock_playlist.shuffle.side_effect = reorder_presets

        with patch("platyplaty.commands.shuffle_playlist.push_undo_snapshot"):
            await execute(mock_ctx)

        # /b.milk was at index 1, now at index 2
        mock_playlist.set_selection.assert_called_with(2)


class TestShufflePreservesPlaying:
    """Tests for shuffle preserving playing state."""

    @pytest.fixture
    def mock_playlist(self):
        """Create a mock Playlist with presets."""
        playlist = MagicMock()
        playlist.presets = [
            Path("/a.milk"),
            Path("/b.milk"),
            Path("/c.milk"),
        ]
        playlist.get_selection.return_value = 0
        playlist.get_playing.return_value = 2  # /c.milk playing
        return playlist

    @pytest.fixture
    def mock_ctx(self, mock_playlist):
        """Create a mock AppContext."""
        ctx = MagicMock()
        ctx.playlist = mock_playlist
        return ctx

    @pytest.mark.asyncio
    async def test_shuffle_preserves_playing_preset(
        self, mock_ctx, mock_playlist
    ):
        """Shuffle keeps the same preset playing."""
        from platyplaty.commands.shuffle_playlist import execute

        # After shuffle, presets list is reordered
        def reorder_presets():
            mock_playlist.presets = [
                Path("/c.milk"),
                Path("/a.milk"),
                Path("/b.milk"),
            ]

        mock_playlist.shuffle.side_effect = reorder_presets

        with patch("platyplaty.commands.shuffle_playlist.push_undo_snapshot"):
            await execute(mock_ctx)

        # /c.milk was at index 2, now at index 0
        mock_playlist.set_playing.assert_called_with(0)
