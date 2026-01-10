#!/usr/bin/env python3
"""Tests for symlink and broken symlink detection.

This module tests the get_entry_type function to verify correct
detection of symlinks and broken symlinks.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.directory_entry import get_entry_type
from platyplaty.ui.directory_types import EntryType


class TestSymlinkDetection:
    """Tests for symlink detection (TASK-1630)."""

    def test_symlink_to_directory_detected(self, tmp_path: Path) -> None:
        """A symlink to a directory is detected as SYMLINK_TO_DIRECTORY."""
        target_dir = tmp_path / "target"
        target_dir.mkdir()
        symlink = tmp_path / "link"
        symlink.symlink_to(target_dir)
        assert get_entry_type(symlink) == EntryType.SYMLINK_TO_DIRECTORY

    def test_symlink_to_file_detected(self, tmp_path: Path) -> None:
        """A symlink to a file is detected as SYMLINK_TO_FILE."""
        target_file = tmp_path / "target.milk"
        target_file.write_text("content")
        symlink = tmp_path / "link.milk"
        symlink.symlink_to(target_file)
        assert get_entry_type(symlink) == EntryType.SYMLINK_TO_FILE


class TestBrokenSymlinkDetection:
    """Tests for broken symlink detection (TASK-1640)."""

    def test_broken_symlink_detected(self, tmp_path: Path) -> None:
        """A symlink to a non-existent target is detected as BROKEN_SYMLINK."""
        symlink = tmp_path / "broken-link.milk"
        symlink.symlink_to(tmp_path / "nonexistent")
        assert get_entry_type(symlink) == EntryType.BROKEN_SYMLINK

    def test_symlink_to_deleted_file_is_broken(self, tmp_path: Path) -> None:
        """A symlink whose target was deleted is detected as BROKEN_SYMLINK."""
        target_file = tmp_path / "target.milk"
        target_file.write_text("content")
        symlink = tmp_path / "link.milk"
        symlink.symlink_to(target_file)
        # Delete the target
        target_file.unlink()
        assert get_entry_type(symlink) == EntryType.BROKEN_SYMLINK

    def test_symlink_to_deleted_directory_is_broken(self, tmp_path: Path) -> None:
        """A symlink whose target directory was deleted is BROKEN_SYMLINK."""
        target_dir = tmp_path / "target"
        target_dir.mkdir()
        symlink = tmp_path / "link"
        symlink.symlink_to(target_dir)
        # Delete the target
        target_dir.rmdir()
        assert get_entry_type(symlink) == EntryType.BROKEN_SYMLINK
