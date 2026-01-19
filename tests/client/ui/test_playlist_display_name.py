#!/usr/bin/env python3
"""Unit tests for playlist display name computation.

Tests the compute_display_names() function which determines how
playlist entries should be displayed, including duplicate filename
disambiguation.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.playlist_display_name import compute_display_names


class TestUniqueFilenames:
    """Tests for entries with unique filenames."""

    def test_single_entry_shows_basename(self) -> None:
        """Single entry shows just the basename."""
        presets = [Path("/home/user/presets/cool.milk")]
        result = compute_display_names(presets)
        assert result == ["cool.milk"]

    def test_multiple_unique_entries(self) -> None:
        """Multiple entries with unique names show basenames."""
        presets = [
            Path("/home/user/presets/cool.milk"),
            Path("/opt/presets/nice.milk"),
            Path("/data/viz/awesome.milk"),
        ]
        result = compute_display_names(presets)
        assert result == ["cool.milk", "nice.milk", "awesome.milk"]

    def test_empty_list(self) -> None:
        """Empty list returns empty list."""
        result = compute_display_names([])
        assert result == []


class TestDuplicateFilenames:
    """Tests for entries with duplicate filenames requiring disambiguation."""

    def test_same_basename_different_parent(self) -> None:
        """Same basename in different directories shows parent to disambiguate."""
        presets = [
            Path("/home/user/presets/a/cool.milk"),
            Path("/home/user/presets/b/cool.milk"),
        ]
        result = compute_display_names(presets)
        assert result == ["a/cool.milk", "b/cool.milk"]

    def test_same_basename_needs_multiple_parents(self) -> None:
        """Same parent requires going up further to disambiguate."""
        presets = [
            Path("/foo/a/b/c/d.milk"),
            Path("/foo/e/b/c/d.milk"),
        ]
        result = compute_display_names(presets)
        assert result == ["a/b/c/d.milk", "e/b/c/d.milk"]

    def test_identical_paths_show_basename_only(self) -> None:
        """Identical full paths show just basename (no disambiguation needed)."""
        presets = [
            Path("/home/user/cool.milk"),
            Path("/home/user/cool.milk"),
        ]
        result = compute_display_names(presets)
        assert result == ["cool.milk", "cool.milk"]

    def test_mixed_unique_and_duplicate(self) -> None:
        """Mix of unique and duplicate filenames handled correctly."""
        presets = [
            Path("/home/user/presets/a/cool.milk"),
            Path("/home/user/presets/b/cool.milk"),
            Path("/home/user/presets/unique.milk"),
        ]
        result = compute_display_names(presets)
        assert result == ["a/cool.milk", "b/cool.milk", "unique.milk"]
