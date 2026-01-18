#!/usr/bin/env python3
"""Unit tests for Playlist load_from_file method."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.playlist import Playlist


class TestLoadFromFile:
    """Tests for load_from_file method."""

    def test_load_from_file_replaces_contents(self, tmp_path: Path) -> None:
        """load_from_file replaces current playlist contents."""
        playlist = Playlist([Path("/old.milk")])
        playlist_file = tmp_path / "test.platy"
        playlist_file.write_text("/new1.milk\n/new2.milk\n")
        playlist.load_from_file(playlist_file)
        assert len(playlist.presets) == 2
        assert playlist.presets[0] == Path("/new1.milk")
        assert playlist.presets[1] == Path("/new2.milk")

    def test_load_from_file_sets_associated_filename(self, tmp_path: Path) -> None:
        """load_from_file sets the associated filename."""
        playlist = Playlist([])
        playlist_file = tmp_path / "test.platy"
        playlist_file.write_text("/a.milk\n")
        playlist.load_from_file(playlist_file)
        assert playlist.associated_filename == playlist_file

    def test_load_from_file_resets_selection_to_zero(self, tmp_path: Path) -> None:
        """load_from_file resets selection to 0."""
        playlist = Playlist([Path("/a.milk"), Path("/b.milk")])
        playlist.set_selection(1)
        playlist_file = tmp_path / "test.platy"
        playlist_file.write_text("/new.milk\n")
        playlist.load_from_file(playlist_file)
        assert playlist.get_selection() == 0

    def test_load_from_file_sets_playing_to_zero(self, tmp_path: Path) -> None:
        """load_from_file sets playing to 0 for non-empty playlist."""
        playlist = Playlist([])
        playlist_file = tmp_path / "test.platy"
        playlist_file.write_text("/a.milk\n")
        playlist.load_from_file(playlist_file)
        assert playlist.get_playing() == 0

    def test_load_from_file_empty_sets_playing_to_none(self, tmp_path: Path) -> None:
        """load_from_file on empty file sets playing to None."""
        playlist = Playlist([Path("/a.milk")])
        playlist_file = tmp_path / "test.platy"
        playlist_file.write_text("")
        playlist.load_from_file(playlist_file)
        assert playlist.get_playing() is None

    def test_load_from_file_clears_dirty_flag(self, tmp_path: Path) -> None:
        """load_from_file clears the dirty flag."""
        playlist = Playlist([Path("/a.milk")])
        playlist.dirty_flag = True
        playlist_file = tmp_path / "test.platy"
        playlist_file.write_text("/new.milk\n")
        playlist.load_from_file(playlist_file)
        assert playlist.dirty_flag is False
