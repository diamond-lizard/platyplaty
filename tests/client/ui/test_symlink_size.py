#!/usr/bin/env python3
"""Unit tests for get_symlink_size function."""

from pathlib import Path

import pytest

from platyplaty.ui.indicators import get_symlink_size


class TestBrokenSymlinkSize:
    """Tests for broken symlink size calculation."""

    def test_broken_symlink_size_is_target_path_length(
        self, tmp_path: Path
    ) -> None:
        """Broken symlink size equals length of target path string."""
        target_path = tmp_path / "nonexistent"
        link = tmp_path / "broken.milk"
        link.symlink_to(target_path)
        # Symlink size is the byte length of the target path string
        expected_size = len(str(target_path).encode())
        assert get_symlink_size(link) == expected_size

    def test_broken_symlink_short_target(self, tmp_path: Path) -> None:
        """Short target path gives small symlink size."""
        link = tmp_path / "link"
        link.symlink_to("x")
        assert get_symlink_size(link) == 1

    def test_broken_symlink_long_target(self, tmp_path: Path) -> None:
        """Long target path gives larger symlink size."""
        long_target = "a" * 100
        link = tmp_path / "link"
        link.symlink_to(long_target)
        assert get_symlink_size(link) == 100


class TestGetSymlinkSizeErrors:
    """Tests for get_symlink_size error handling (TASK-3600)."""

    def test_nonexistent_symlink_returns_zero(self) -> None:
        """Non-existent symlink returns 0."""
        nonexistent = Path("/nonexistent/symlink/12345")
        assert get_symlink_size(nonexistent) == 0

    def test_deleted_symlink_returns_zero(self, tmp_path: Path) -> None:
        """Symlink deleted after path created returns 0."""
        link = tmp_path / "link"
        link.symlink_to("target")
        link.unlink()
        assert get_symlink_size(link) == 0

    def test_permission_denied_returns_zero(self, tmp_path: Path) -> None:
        """Symlink in inaccessible directory returns 0."""
        restricted_dir = tmp_path / "restricted_dir"
        restricted_dir.mkdir()
        link = restricted_dir / "link"
        link.symlink_to("target")
        restricted_dir.chmod(0o000)
        try:
            assert get_symlink_size(link) == 0
        finally:
            restricted_dir.chmod(0o755)
