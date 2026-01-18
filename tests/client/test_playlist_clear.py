#!/usr/bin/env python3
"""Unit tests for Playlist clear method."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.playlist import Playlist


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
