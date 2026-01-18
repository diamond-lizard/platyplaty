#!/usr/bin/env python3
"""Unit tests for Playlist save_to_file method."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.playlist import Playlist


class TestSaveToFile:
    """Tests for save_to_file method."""

    def test_save_to_file_writes_presets(self, tmp_path: Path) -> None:
        """save_to_file writes presets to file."""
        playlist = Playlist([Path("/a.milk"), Path("/b.milk")])
        playlist_file = tmp_path / "test.platy"
        playlist.save_to_file(playlist_file)
        content = playlist_file.read_text()
        assert "/a.milk" in content
        assert "/b.milk" in content

    def test_save_to_file_updates_associated_filename(self, tmp_path: Path) -> None:
        """save_to_file updates the associated filename."""
        playlist = Playlist([Path("/a.milk")])
        playlist_file = tmp_path / "new.platy"
        playlist.save_to_file(playlist_file)
        assert playlist.associated_filename == playlist_file

    def test_save_to_file_clears_dirty_flag(self, tmp_path: Path) -> None:
        """save_to_file clears the dirty flag."""
        playlist = Playlist([Path("/a.milk")])
        playlist.dirty_flag = True
        playlist_file = tmp_path / "test.platy"
        playlist.save_to_file(playlist_file)
        assert playlist.dirty_flag is False

    def test_save_to_file_without_path_uses_associated(self, tmp_path: Path) -> None:
        """save_to_file without path uses associated filename."""
        playlist = Playlist([Path("/a.milk")])
        playlist_file = tmp_path / "test.platy"
        playlist.associated_filename = playlist_file
        playlist.save_to_file()
        assert playlist_file.exists()
        assert "/a.milk" in playlist_file.read_text()

    def test_save_to_file_without_path_or_associated_raises(self) -> None:
        """save_to_file without path and no associated raises ValueError."""
        playlist = Playlist([Path("/a.milk")])
        with pytest.raises(ValueError, match="No file name"):
            playlist.save_to_file()
