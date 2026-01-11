#!/usr/bin/env python3
"""Unit tests for count_directory_contents function."""

from pathlib import Path

import pytest

from platyplaty.ui.indicators import count_directory_contents


class TestCountDirectoryContents:
    """Tests for count_directory_contents function."""

    def test_empty_directory(self, tmp_path: Path) -> None:
        """Empty directory returns 0."""
        assert count_directory_contents(tmp_path) == 0

    def test_counts_directories(self, tmp_path: Path) -> None:
        """Counts subdirectories."""
        (tmp_path / "subdir1").mkdir()
        (tmp_path / "subdir2").mkdir()
        assert count_directory_contents(tmp_path) == 2

    def test_counts_milk_files(self, tmp_path: Path) -> None:
        """Counts .milk files."""
        (tmp_path / "preset1.milk").write_text("content")
        (tmp_path / "preset2.milk").write_text("content")
        (tmp_path / "preset3.MILK").write_text("content")
        assert count_directory_contents(tmp_path) == 3

    def test_excludes_non_milk_files(self, tmp_path: Path) -> None:
        """Non-.milk files are excluded from count."""
        (tmp_path / "readme.txt").write_text("content")
        (tmp_path / "image.png").write_text("content")
        (tmp_path / "preset.milk").write_text("content")
        assert count_directory_contents(tmp_path) == 1

    def test_mixed_content(self, tmp_path: Path) -> None:
        """Counts both directories and .milk files."""
        (tmp_path / "subdir").mkdir()
        (tmp_path / "preset.milk").write_text("content")
        (tmp_path / "other.txt").write_text("excluded")
        assert count_directory_contents(tmp_path) == 2


class TestVisibilityFilter:
    """Tests that count matches the visibility filter specification."""

    def test_symlink_to_directory_counted(self, tmp_path: Path) -> None:
        """Symlinks to directories are counted."""
        target = tmp_path / "target_dir"
        target.mkdir()
        link = tmp_path / "link_to_dir"
        link.symlink_to(target)
        # Should count both target_dir and link_to_dir
        assert count_directory_contents(tmp_path) == 2

    def test_symlink_to_milk_file_counted(self, tmp_path: Path) -> None:
        """Symlinks to .milk files are counted."""
        target = tmp_path / "target.milk"
        target.write_text("content")
        link = tmp_path / "link.milk"
        link.symlink_to(target)
        assert count_directory_contents(tmp_path) == 2

    def test_symlink_to_non_milk_excluded(self, tmp_path: Path) -> None:
        """Symlinks to non-.milk files are excluded."""
        target = tmp_path / "target.txt"
        target.write_text("content")
        link = tmp_path / "link.txt"
        link.symlink_to(target)
        assert count_directory_contents(tmp_path) == 0

    def test_broken_symlink_milk_extension_counted(
        self, tmp_path: Path
    ) -> None:
        """Broken symlinks with .milk extension are counted."""
        link = tmp_path / "broken.milk"
        link.symlink_to(tmp_path / "nonexistent")
        assert count_directory_contents(tmp_path) == 1

    def test_broken_symlink_no_extension_counted(
        self, tmp_path: Path
    ) -> None:
        """Broken symlinks with no extension are counted."""
        link = tmp_path / "broken_link"
        link.symlink_to(tmp_path / "nonexistent")
        assert count_directory_contents(tmp_path) == 1

    def test_broken_symlink_other_extension_excluded(
        self, tmp_path: Path
    ) -> None:
        """Broken symlinks with other extensions are excluded."""
        link = tmp_path / "broken.txt"
        link.symlink_to(tmp_path / "nonexistent")
        assert count_directory_contents(tmp_path) == 0


