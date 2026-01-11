#!/usr/bin/env python3
"""Unit tests for get_file_size function."""

from pathlib import Path

import pytest

from platyplaty.ui.size_format import get_file_size


class TestGetFileSizeNormal:
    """Tests for normal file size retrieval."""

    def test_returns_file_size(self, tmp_path: Path) -> None:
        """Returns size of existing file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello")
        assert get_file_size(test_file) == 5

    def test_empty_file(self, tmp_path: Path) -> None:
        """Empty file returns 0."""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")
        assert get_file_size(test_file) == 0


class TestGetFileSizeErrors:
    """Tests for get_file_size error handling (TASK-3500)."""

    def test_nonexistent_file_returns_zero(self) -> None:
        """Non-existent file returns 0."""
        nonexistent = Path("/nonexistent/file/12345.txt")
        assert get_file_size(nonexistent) == 0

    def test_deleted_file_returns_zero(self, tmp_path: Path) -> None:
        """File deleted after path created returns 0."""
        test_file = tmp_path / "deleted.txt"
        test_file.write_text("content")
        test_file.unlink()
        assert get_file_size(test_file) == 0

    def test_permission_denied_returns_zero(self, tmp_path: Path) -> None:
        """File in inaccessible directory returns 0."""
        restricted_dir = tmp_path / "restricted_dir"
        restricted_dir.mkdir()
        test_file = restricted_dir / "file.txt"
        test_file.write_text("content")
        restricted_dir.chmod(0o000)
        try:
            assert get_file_size(test_file) == 0
        finally:
            restricted_dir.chmod(0o755)
