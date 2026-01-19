#!/usr/bin/env python3
"""Unit tests for skip logic with broken presets."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.autoplay_helpers import find_next_playable, is_preset_playable
from platyplaty.playlist import Playlist


class TestIsPresetPlayable:
    """Tests for is_preset_playable function."""

    def test_existing_file_is_playable(self, tmp_path: Path) -> None:
        """Existing regular file is playable."""
        preset = tmp_path / "test.milk"
        preset.touch()
        assert is_preset_playable(preset) is True

    def test_nonexistent_file_is_not_playable(self, tmp_path: Path) -> None:
        """Nonexistent file is not playable."""
        preset = tmp_path / "missing.milk"
        assert is_preset_playable(preset) is False

    def test_broken_symlink_is_not_playable(self, tmp_path: Path) -> None:
        """Broken symlink is not playable."""
        link = tmp_path / "broken.milk"
        link.symlink_to(tmp_path / "nonexistent.milk")
        assert is_preset_playable(link) is False

    def test_valid_symlink_is_playable(self, tmp_path: Path) -> None:
        """Valid symlink to existing file is playable."""
        target = tmp_path / "target.milk"
        target.touch()
        link = tmp_path / "link.milk"
        link.symlink_to(target)
        assert is_preset_playable(link) is True


class TestFindNextPlayable:
    """Tests for find_next_playable function."""

    def test_find_next_in_sequence(self, tmp_path: Path) -> None:
        """find_next_playable finds the next valid preset."""
        a = tmp_path / "a.milk"
        b = tmp_path / "b.milk"
        a.touch()
        b.touch()
        result = find_next_playable(Playlist([a, b]), 0)
        assert result == 1

    def test_skip_broken_preset(self, tmp_path: Path) -> None:
        """find_next_playable skips broken presets."""
        a = tmp_path / "a.milk"
        broken = tmp_path / "broken.milk"
        c = tmp_path / "c.milk"
        a.touch()
        c.touch()
        # broken is not touched, so it doesn't exist
        result = find_next_playable(Playlist([a, broken, c]), 0)
        assert result == 2  # Skips index 1 (broken)

    def test_returns_none_when_all_broken(self, tmp_path: Path) -> None:
        """find_next_playable returns None when all presets broken."""
        a = tmp_path / "a.milk"
        b = tmp_path / "b.milk"
        # Neither file exists
        result = find_next_playable(Playlist([a, b]), 0)
        assert result is None

    def test_empty_list_returns_none(self) -> None:
        """find_next_playable returns None for empty list."""
        result = find_next_playable(Playlist([]), 0)
        assert result is None
