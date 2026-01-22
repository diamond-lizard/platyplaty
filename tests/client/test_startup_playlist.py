#!/usr/bin/env python3
"""Unit tests for startup playlist loading.

Tests _create_playlist function and playlist argument handling.
"""

import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.errors import StartupError
from platyplaty.run_sequence import _create_playlist


class TestCreatePlaylist:
    """Tests for _create_playlist function."""

    def test_no_path_returns_empty_playlist(self) -> None:
        """With no path, returns empty playlist."""
        playlist = _create_playlist(None)
        assert len(playlist.presets) == 0
        assert playlist.loop is True

    def test_valid_playlist_file_loads_presets(self, tmp_path: Path) -> None:
        """With valid playlist file, loads presets."""
        preset1 = tmp_path / "a.milk"
        preset2 = tmp_path / "b.milk"
        preset1.touch()
        preset2.touch()
        playlist_file = tmp_path / "test.platy"
        playlist_file.write_text(f"{preset1}\n{preset2}\n")
        playlist = _create_playlist(playlist_file)
        assert len(playlist.presets) == 2
        assert playlist.presets[0] == preset1
        assert playlist.presets[1] == preset2

    def test_valid_playlist_sets_selection_index_zero(
        self, tmp_path: Path
    ) -> None:
        """Loaded playlist has selection_index 0."""
        preset = tmp_path / "a.milk"
        preset.touch()
        playlist_file = tmp_path / "test.platy"
        playlist_file.write_text(f"{preset}\n")
        playlist = _create_playlist(playlist_file)
        assert playlist._selection_index == 0

    def test_valid_playlist_sets_playing_index_zero(
        self, tmp_path: Path
    ) -> None:
        """Loaded playlist has playing_index 0."""
        preset = tmp_path / "a.milk"
        preset.touch()
        playlist_file = tmp_path / "test.platy"
        playlist_file.write_text(f"{preset}\n")
        playlist = _create_playlist(playlist_file)
        assert playlist._playing_index == 0

    def test_nonexistent_file_raises_startup_error(self) -> None:
        """Nonexistent playlist file raises StartupError."""
        with pytest.raises(StartupError) as exc_info:
            _create_playlist(Path("/nonexistent/path.platy"))
        assert "Could not load playlist" in str(exc_info.value)

    def test_empty_playlist_file_returns_empty(self, tmp_path: Path) -> None:
        """Empty playlist file returns empty playlist."""
        playlist_file = tmp_path / "empty.platy"
        playlist_file.write_text("")
        playlist = _create_playlist(playlist_file)
        assert len(playlist.presets) == 0
        assert playlist._playing_index is None
