#!/usr/bin/env python3
"""Edge case tests for count_directory_contents function.

Tests for inaccessible directories and symlinks to directories.
"""

from pathlib import Path

import pytest

from platyplaty.ui.indicators import count_directory_contents


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
