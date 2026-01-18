#!/usr/bin/env python3
"""Unit tests for Playlist selection and playing index management."""

import sys
from pathlib import Path
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
