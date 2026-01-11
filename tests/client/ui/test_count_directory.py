#!/usr/bin/env python3
"""Unit tests for count_directory_contents function.

Tests the directory counting function that counts entries matching
the visibility filter (directories, .milk files, valid symlinks,
and qualifying broken symlinks).
"""

import os
import stat
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


class TestInaccessibleDirectory:
    """Tests for inaccessible directory handling."""

    def test_permission_denied_returns_zero(self, tmp_path: Path) -> None:
        """Inaccessible directory returns 0."""
        restricted = tmp_path / "restricted"
        restricted.mkdir()
        (restricted / "file.milk").write_text("content")
        # Remove read permission
        restricted.chmod(0o000)
        try:
            assert count_directory_contents(restricted) == 0
        finally:
            # Restore permissions for cleanup
            restricted.chmod(0o755)

    def test_nonexistent_directory_returns_zero(self) -> None:
        """Non-existent directory returns 0."""
        nonexistent = Path("/nonexistent/path/12345")
        assert count_directory_contents(nonexistent) == 0


class TestSymlinkToDirectory:
    """Tests for symlinks to directories counting target contents."""

    def test_symlink_counts_target_contents(self, tmp_path: Path) -> None:
        """Symlink to directory counts the target's contents."""
        # Create target directory with files
        target = tmp_path / "target_dir"
        target.mkdir()
        (target / "file1.milk").write_text("content")
        (target / "file2.milk").write_text("content")
        (target / "subdir").mkdir()
        # Create symlink to target
        link = tmp_path / "link_to_dir"
        link.symlink_to(target)
        # Counting the symlink should count target's contents (3 items)
        assert count_directory_contents(link) == 3
