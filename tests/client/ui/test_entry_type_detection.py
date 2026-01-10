#!/usr/bin/env python3
"""Tests for entry type detection.

This module tests the get_entry_type function to verify correct
detection of directories, files, symlinks, and broken symlinks.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.directory_entry import get_entry_type
from platyplaty.ui.directory_types import EntryType


class TestDirectoryDetection:
    """Tests for directory detection (TASK-1610)."""

    def test_regular_directory_detected(self, tmp_path: Path) -> None:
        """A regular directory is detected as DIRECTORY."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        assert get_entry_type(subdir) == EntryType.DIRECTORY

    def test_symlink_to_directory_not_detected_as_directory(
        self, tmp_path: Path
    ) -> None:
        """A symlink to a directory should not be DIRECTORY type."""
        target_dir = tmp_path / "target"
        target_dir.mkdir()
        symlink = tmp_path / "link"
        symlink.symlink_to(target_dir)
        # Should be SYMLINK_TO_DIRECTORY, not DIRECTORY
        assert get_entry_type(symlink) != EntryType.DIRECTORY
        assert get_entry_type(symlink) == EntryType.SYMLINK_TO_DIRECTORY


class TestFileDetection:
    """Tests for file detection (TASK-1620)."""

    def test_regular_file_detected(self, tmp_path: Path) -> None:
        """A regular file is detected as FILE."""
        test_file = tmp_path / "test.milk"
        test_file.write_text("content")
        assert get_entry_type(test_file) == EntryType.FILE

    def test_symlink_to_file_not_detected_as_file(
        self, tmp_path: Path
    ) -> None:
        """A symlink to a file should not be FILE type."""
        target_file = tmp_path / "target.milk"
        target_file.write_text("content")
        symlink = tmp_path / "link.milk"
        symlink.symlink_to(target_file)
        # Should be SYMLINK_TO_FILE, not FILE
        assert get_entry_type(symlink) != EntryType.FILE
        assert get_entry_type(symlink) == EntryType.SYMLINK_TO_FILE

