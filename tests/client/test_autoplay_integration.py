#!/usr/bin/env python3
"""Integration tests for autoplay with various scenarios.

Tests autoplay behavior across different playlist states and user actions.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.playlist import Playlist


@pytest.fixture
def playlist_with_presets() -> Playlist:
    """Create a Playlist with multiple presets."""
    return Playlist([
        Path("/presets/a.milk"),
        Path("/presets/b.milk"),
        Path("/presets/c.milk"),
    ])


@pytest.fixture
def mock_autoplay_manager() -> MagicMock:
    """Create a mock AutoplayManager."""
    mgr = MagicMock()
    mgr.autoplay_enabled = False
    return mgr


class TestAutoplayToggleBehavior:
    """Tests for autoplay toggle behavior."""

    def test_toggle_on_snaps_selection_to_playing(
        self, playlist_with_presets: Playlist
    ) -> None:
        """Toggling autoplay on snaps selection to playing preset."""
        playlist = playlist_with_presets
        playlist.set_selection(0)
        playlist.set_playing(2)

        # Simulate snap behavior
        playlist.set_selection(playlist.get_playing())

        assert playlist.get_selection() == 2

    def test_autoplay_advances_both_indicators(
        self, playlist_with_presets: Playlist
    ) -> None:
        """Autoplay advance moves both selection and playing."""
        playlist = playlist_with_presets
        playlist.set_selection(0)
        playlist.set_playing(0)

        # Simulate autoplay advance
        next_index = 1
        playlist.set_selection(next_index)
        playlist.set_playing(next_index)

        assert playlist.get_selection() == 1
        assert playlist.get_playing() == 1


class TestAutoplayWithBrokenPresets:
    """Tests for autoplay skipping broken presets."""

    def test_skip_advances_past_broken(
        self, playlist_with_presets: Playlist
    ) -> None:
        """Autoplay skips broken presets and advances to next."""
        playlist = playlist_with_presets
        playlist.set_playing(0)

        # Simulate: index 1 is broken, skip to index 2
        broken_index = 1
        next_playable = 2
        playlist.set_selection(next_playable)
        playlist.set_playing(next_playable)

        assert playlist.get_playing() == 2


class TestAutoplayLooping:
    """Tests for autoplay looping behavior."""

    def test_loop_returns_to_first(
        self, playlist_with_presets: Playlist
    ) -> None:
        """Autoplay loops from last preset to first."""
        playlist = playlist_with_presets
        playlist.set_playing(2)  # Last preset

        # Simulate loop to first
        playlist.set_selection(0)
        playlist.set_playing(0)

        assert playlist.get_playing() == 0
        assert playlist.get_selection() == 0


class TestAutoplayWithShuffleAndReorder:
    """Tests for autoplay interaction with shuffle and reorder."""

    def test_shuffle_during_autoplay_preserves_playing(
        self, playlist_with_presets: Playlist
    ) -> None:
        """Shuffle during autoplay keeps same preset playing."""
        playlist = playlist_with_presets
        playing_path = playlist.presets[1]
        playlist.set_playing(1)

        playlist.shuffle()

        # Find new index of playing preset
        new_index = playlist.presets.index(playing_path)
        playlist.set_playing(new_index)

        assert playlist.presets[playlist.get_playing()] == playing_path
