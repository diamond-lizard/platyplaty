#!/usr/bin/env python3
"""Unit tests for mark_all_matching_as_broken function."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.playlist import Playlist
from platyplaty.playlist_broken import mark_all_matching_as_broken


class TestMarkAllMatchingAsBroken:
    """Tests for mark_all_matching_as_broken function."""

    def test_single_match(self, tmp_path: Path) -> None:
        """Marks single matching preset as broken."""
        preset1 = tmp_path / "a.milk"
        preset2 = tmp_path / "b.milk"
        preset3 = tmp_path / "c.milk"
        for p in [preset1, preset2, preset3]:
            p.touch()
        playlist = Playlist([preset1, preset2, preset3])
        mark_all_matching_as_broken(playlist, preset2)
        assert playlist.broken_indices == {1}

    def test_multiple_matches(self, tmp_path: Path) -> None:
        """Marks all copies of preset as broken."""
        preset1 = tmp_path / "a.milk"
        preset2 = tmp_path / "b.milk"
        for p in [preset1, preset2]:
            p.touch()
        playlist = Playlist([preset1, preset2, preset1, preset2, preset1])
        mark_all_matching_as_broken(playlist, preset1)
        assert playlist.broken_indices == {0, 2, 4}

    def test_no_matches(self, tmp_path: Path) -> None:
        """No change when preset not in playlist."""
        preset1 = tmp_path / "a.milk"
        preset2 = tmp_path / "b.milk"
        preset3 = tmp_path / "c.milk"
        for p in [preset1, preset2, preset3]:
            p.touch()
        playlist = Playlist([preset1, preset2])
        mark_all_matching_as_broken(playlist, preset3)
        assert playlist.broken_indices == set()

    def test_symlinks_resolve_to_same_path(self, tmp_path: Path) -> None:
        """Symlinks to same target are all marked as broken."""
        original = tmp_path / "original.milk"
        original.touch()
        link1 = tmp_path / "link1.milk"
        link2 = tmp_path / "link2.milk"
        link1.symlink_to(original)
        link2.symlink_to(original)
        playlist = Playlist([original, link1, link2])
        mark_all_matching_as_broken(playlist, link1)
        assert playlist.broken_indices == {0, 1, 2}

    def test_preserves_existing_broken_indices(self, tmp_path: Path) -> None:
        """Existing broken indices are preserved."""
        preset1 = tmp_path / "a.milk"
        preset2 = tmp_path / "b.milk"
        for p in [preset1, preset2]:
            p.touch()
        playlist = Playlist([preset1, preset2])
        playlist.broken_indices.add(0)
        mark_all_matching_as_broken(playlist, preset2)
        assert playlist.broken_indices == {0, 1}
