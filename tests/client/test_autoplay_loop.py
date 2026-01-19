#!/usr/bin/env python3
"""Unit tests for autoplay looping behavior."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.autoplay_helpers import find_next_playable
from platyplaty.playlist import Playlist


class TestLoopingBehavior:
    """Tests for playlist looping in find_next_playable."""

    def test_loops_from_last_to_first(self, tmp_path: Path) -> None:
        """find_next_playable loops from last preset to first."""
        a = tmp_path / "a.milk"
        b = tmp_path / "b.milk"
        c = tmp_path / "c.milk"
        a.touch()
        b.touch()
        c.touch()
        # Starting from last preset (index 2), should loop to first (index 0)
        result = find_next_playable(Playlist([a, b, c]), 2)
        assert result == 0

    def test_loops_skipping_broken_at_start(self, tmp_path: Path) -> None:
        """find_next_playable loops and skips broken preset at start."""
        broken = tmp_path / "broken.milk"  # Not created
        b = tmp_path / "b.milk"
        c = tmp_path / "c.milk"
        b.touch()
        c.touch()
        # Starting from last (index 2), first is broken, should find second (index 1)
        result = find_next_playable(Playlist([broken, b, c]), 2)
        assert result == 1

    def test_single_preset_returns_same_index(self, tmp_path: Path) -> None:
        """Single playable preset returns same index (no reload)."""
        a = tmp_path / "a.milk"
        a.touch()
        result = find_next_playable(Playlist([a]), 0)
        assert result == 0

    def test_loops_around_entire_playlist(self, tmp_path: Path) -> None:
        """find_next_playable checks entire playlist when looping."""
        a = tmp_path / "a.milk"
        broken1 = tmp_path / "broken1.milk"
        broken2 = tmp_path / "broken2.milk"
        a.touch()
        # Starting from index 0, skips 1 and 2, loops back to 0
        result = find_next_playable(Playlist([a, broken1, broken2]), 0)
        assert result == 0

    def test_finds_only_playable_after_loop(self, tmp_path: Path) -> None:
        """find_next_playable finds playable preset after looping past broken."""
        a = tmp_path / "a.milk"
        broken = tmp_path / "broken.milk"
        a.touch()
        # Starting from index 1 (broken), loops to find index 0
        result = find_next_playable(Playlist([a, broken]), 1)
        assert result == 0
