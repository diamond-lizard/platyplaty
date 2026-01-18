#!/usr/bin/env python3
"""Unit tests for Playlist move_preset_up and move_preset_down methods."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.playlist import Playlist


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
