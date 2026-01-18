#!/usr/bin/env python3
"""Unit tests for Playlist add_preset and remove_preset methods."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.playlist import Playlist


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
