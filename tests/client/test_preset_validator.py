#!/usr/bin/env python3
"""Unit tests for preset validation functions.

Tests is_broken_symlink(), is_readable(), and is_valid_preset()
functions from preset_validator module.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.preset_validator import (
    is_broken_symlink,
    is_readable,
    is_valid_preset,
)


class TestIsBrokenSymlink:
    """Tests for is_broken_symlink function."""

    def test_regular_file_not_broken(self, tmp_path: Path) -> None:
        """Regular file is not a broken symlink."""
        f = tmp_path / "test.milk"
        f.write_text("content")
        assert is_broken_symlink(f) is False

    def test_valid_symlink_not_broken(self, tmp_path: Path) -> None:
        """Symlink pointing to existing file is not broken."""
        target = tmp_path / "target.milk"
        target.write_text("content")
        link = tmp_path / "link.milk"
        link.symlink_to(target)
        assert is_broken_symlink(link) is False

    def test_broken_symlink_is_broken(self, tmp_path: Path) -> None:
        """Symlink pointing to non-existent file is broken."""
        link = tmp_path / "broken.milk"
        link.symlink_to(tmp_path / "nonexistent.milk")
        assert is_broken_symlink(link) is True

    def test_nonexistent_file_not_broken(self, tmp_path: Path) -> None:
        """Non-existent file is not a broken symlink (it's not a symlink)."""
        f = tmp_path / "nonexistent.milk"
        assert is_broken_symlink(f) is False


class TestIsReadable:
    """Tests for is_readable function."""

    def test_readable_file(self, tmp_path: Path) -> None:
        """Readable file returns True."""
        f = tmp_path / "test.milk"
        f.write_text("content")
        assert is_readable(f) is True

    def test_nonexistent_file(self, tmp_path: Path) -> None:
        """Non-existent file returns False."""
        f = tmp_path / "nonexistent.milk"
        assert is_readable(f) is False

    def test_unreadable_file(self, tmp_path: Path) -> None:
        """Unreadable file returns False."""
        f = tmp_path / "unreadable.milk"
        f.write_text("content")
        f.chmod(0o000)
        try:
            assert is_readable(f) is False
        finally:
            f.chmod(0o644)


class TestIsValidPreset:
    """Tests for is_valid_preset function."""

    def test_valid_regular_file(self, tmp_path: Path) -> None:
        """Regular readable file is valid."""
        f = tmp_path / "test.milk"
        f.write_text("content")
        assert is_valid_preset(f) is True

    def test_valid_symlink(self, tmp_path: Path) -> None:
        """Symlink to readable file is valid."""
        target = tmp_path / "target.milk"
        target.write_text("content")
        link = tmp_path / "link.milk"
        link.symlink_to(target)
        assert is_valid_preset(link) is True

    def test_broken_symlink_invalid(self, tmp_path: Path) -> None:
        """Broken symlink is invalid."""
        link = tmp_path / "broken.milk"
        link.symlink_to(tmp_path / "nonexistent.milk")
        assert is_valid_preset(link) is False

    def test_nonexistent_file_invalid(self, tmp_path: Path) -> None:
        """Non-existent file is invalid."""
        f = tmp_path / "nonexistent.milk"
        assert is_valid_preset(f) is False

    def test_unreadable_file_invalid(self, tmp_path: Path) -> None:
        """Unreadable file returns False."""
        f = tmp_path / "unreadable.milk"
        f.write_text("content")
        f.chmod(0o000)
        try:
            assert is_valid_preset(f) is False
        finally:
            f.chmod(0o644)
