#!/usr/bin/env python3
"""Integration tests for full playlist workflow.

Tests for workflow sequences:
- Load playlist, browse, add presets, shuffle, save
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.playlist import Playlist


@pytest.fixture
def real_playlist() -> Playlist:
    """Create a real Playlist instance for integration tests."""
    return Playlist([
        Path("/presets/a.milk"),
        Path("/presets/b.milk"),
        Path("/presets/c.milk"),
    ])


@pytest.fixture
def mock_ctx_with_real_playlist(real_playlist: Playlist) -> MagicMock:
    """Create a mock AppContext using a real Playlist."""
    ctx = MagicMock()
    ctx.playlist = real_playlist
    ctx.undo_manager = MagicMock()
    ctx.autoplay_manager = MagicMock()
    ctx.autoplay_manager.autoplay_enabled = False
    return ctx


class TestLoadAndAddWorkflow:
    """Tests for load playlist then add preset workflow."""

    def test_load_then_add_preset_marks_dirty(
        self, mock_ctx_with_real_playlist: MagicMock
    ) -> None:
        """Loading playlist then adding preset marks it dirty."""
        ctx = mock_ctx_with_real_playlist
        playlist = ctx.playlist

        # Initial state: not dirty (just loaded)
        playlist.dirty_flag = False

        # Add a preset
        new_path = Path("/presets/new.milk")
        playlist.add_preset(new_path)

        assert playlist.dirty_flag is True
        assert new_path in playlist.presets
        assert len(playlist.presets) == 4


class TestAddShuffleSaveWorkflow:
    """Tests for add, shuffle, then save workflow."""

    def test_shuffle_preserves_all_presets(
        self, mock_ctx_with_real_playlist: MagicMock
    ) -> None:
        """Shuffle preserves all presets in the playlist."""
        playlist = mock_ctx_with_real_playlist.playlist
        original_presets = set(playlist.presets)

        playlist.shuffle()

        assert set(playlist.presets) == original_presets

    def test_save_clears_dirty_flag(
        self, mock_ctx_with_real_playlist: MagicMock, tmp_path: Path
    ) -> None:
        """Saving clears the dirty flag."""
        playlist = mock_ctx_with_real_playlist.playlist
        playlist.add_preset(Path("/presets/d.milk"))
        playlist.dirty_flag = True

        save_path = tmp_path / "test.platy"
        playlist.save_to_file(save_path)

        assert playlist.dirty_flag is False
        assert playlist.associated_filename == save_path


class TestBrowseAndPreviewWorkflow:
    """Tests for browsing and previewing presets."""

    def test_selection_independent_of_playing(
        self, mock_ctx_with_real_playlist: MagicMock
    ) -> None:
        """Selection and playing indices are independent."""
        playlist = mock_ctx_with_real_playlist.playlist

        playlist.set_selection(0)
        playlist.set_playing(2)

        assert playlist.get_selection() == 0
        assert playlist.get_playing() == 2

        # Move selection without affecting playing
        playlist.set_selection(1)
        assert playlist.get_selection() == 1
        assert playlist.get_playing() == 2
