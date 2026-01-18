#!/usr/bin/env python3
"""Unit tests for Playlist class methods.

Tests the Playlist class state management: selection, playing,
add/remove/move presets, clear, load, and save operations.
"""

import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.playlist import Playlist


class TestSelectionAndPlaying:
    """Tests for selection and playing index management."""

    def test_get_selection_default(self) -> None:
        """New playlist has selection at 0."""
        playlist = Playlist([Path("/a.milk"), Path("/b.milk")])
        assert playlist.get_selection() == 0

    def test_set_selection(self) -> None:
        """set_selection changes the selection index."""
        playlist = Playlist([Path("/a.milk"), Path("/b.milk")])
        playlist.set_selection(1)
        assert playlist.get_selection() == 1

    def test_get_playing_default(self) -> None:
        """New non-empty playlist has playing at 0."""
        playlist = Playlist([Path("/a.milk"), Path("/b.milk")])
        assert playlist.get_playing() == 0

    def test_set_playing(self) -> None:
        """set_playing changes the playing index."""
        playlist = Playlist([Path("/a.milk"), Path("/b.milk")])
        playlist.set_playing(1)
        assert playlist.get_playing() == 1

    def test_set_playing_none(self) -> None:
        """set_playing to None means idle preset."""
        playlist = Playlist([Path("/a.milk"), Path("/b.milk")])
        playlist.set_playing(None)
        assert playlist.get_playing() is None


class TestAddRemovePreset:
    """Tests for add_preset and remove_preset methods."""

    def test_add_preset_appends_to_end(self) -> None:
        """add_preset adds at the end of the playlist."""
        playlist = Playlist([Path("/a.milk")])
        playlist.add_preset(Path("/b.milk"))
        assert len(playlist.presets) == 2
        assert playlist.presets[1] == Path("/b.milk")

    def test_add_preset_sets_dirty_flag(self) -> None:
        """add_preset sets the dirty flag."""
        playlist = Playlist([Path("/a.milk")])
        playlist.dirty_flag = False
        playlist.add_preset(Path("/b.milk"))
        assert playlist.dirty_flag is True

    def test_add_preset_allows_duplicates(self) -> None:
        """add_preset allows duplicate entries."""
        playlist = Playlist([Path("/a.milk")])
        playlist.add_preset(Path("/a.milk"))
        assert len(playlist.presets) == 2
        assert playlist.presets[0] == playlist.presets[1]

    def test_remove_preset(self) -> None:
        """remove_preset removes at the given index."""
        playlist = Playlist([Path("/a.milk"), Path("/b.milk")])
        playlist.remove_preset(0)
        assert len(playlist.presets) == 1
        assert playlist.presets[0] == Path("/b.milk")

    def test_remove_preset_sets_dirty_flag(self) -> None:
        """remove_preset sets the dirty flag."""
        playlist = Playlist([Path("/a.milk"), Path("/b.milk")])
        playlist.dirty_flag = False
        playlist.remove_preset(0)
        assert playlist.dirty_flag is True


class TestMovePreset:
    """Tests for move_preset_up and move_preset_down methods."""

    def test_move_preset_up(self) -> None:
        """move_preset_up swaps with previous item."""
        playlist = Playlist([Path("/a.milk"), Path("/b.milk")])
        result = playlist.move_preset_up(1)
        assert result is True
        assert playlist.presets[0] == Path("/b.milk")
        assert playlist.presets[1] == Path("/a.milk")

    def test_move_preset_up_at_top_returns_false(self) -> None:
        """move_preset_up at index 0 returns False."""
        playlist = Playlist([Path("/a.milk"), Path("/b.milk")])
        result = playlist.move_preset_up(0)
        assert result is False
        assert playlist.presets[0] == Path("/a.milk")

    def test_move_preset_up_sets_dirty_flag(self) -> None:
        """move_preset_up sets the dirty flag."""
        playlist = Playlist([Path("/a.milk"), Path("/b.milk")])
        playlist.dirty_flag = False
        playlist.move_preset_up(1)
        assert playlist.dirty_flag is True

    def test_move_preset_down(self) -> None:
        """move_preset_down swaps with next item."""
        playlist = Playlist([Path("/a.milk"), Path("/b.milk")])
        result = playlist.move_preset_down(0)
        assert result is True
        assert playlist.presets[0] == Path("/b.milk")
        assert playlist.presets[1] == Path("/a.milk")

    def test_move_preset_down_at_bottom_returns_false(self) -> None:
        """move_preset_down at last index returns False."""
        playlist = Playlist([Path("/a.milk"), Path("/b.milk")])
        result = playlist.move_preset_down(1)
        assert result is False
        assert playlist.presets[1] == Path("/b.milk")

    def test_move_preset_down_sets_dirty_flag(self) -> None:
        """move_preset_down sets the dirty flag."""
        playlist = Playlist([Path("/a.milk"), Path("/b.milk")])
        playlist.dirty_flag = False
        playlist.move_preset_down(0)
        assert playlist.dirty_flag is True


class TestClear:
    """Tests for clear method."""

    def test_clear_removes_all_presets(self) -> None:
        """clear removes all presets."""
        playlist = Playlist([Path("/a.milk"), Path("/b.milk")])
        playlist.clear()
        assert len(playlist.presets) == 0

    def test_clear_clears_associated_filename(self) -> None:
        """clear clears the associated filename."""
        playlist = Playlist([Path("/a.milk")])
        playlist.associated_filename = Path("/test.platy")
        playlist.clear()
        assert playlist.associated_filename is None

    def test_clear_resets_selection_to_zero(self) -> None:
        """clear resets selection index to 0."""
        playlist = Playlist([Path("/a.milk"), Path("/b.milk")])
        playlist.set_selection(1)
        playlist.clear()
        assert playlist.get_selection() == 0

    def test_clear_sets_playing_to_none(self) -> None:
        """clear sets playing index to None (idle)."""
        playlist = Playlist([Path("/a.milk"), Path("/b.milk")])
        playlist.clear()
        assert playlist.get_playing() is None

    def test_clear_sets_dirty_flag(self) -> None:
        """clear sets the dirty flag."""
        playlist = Playlist([Path("/a.milk")])
        playlist.dirty_flag = False
        playlist.clear()
        assert playlist.dirty_flag is True


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
