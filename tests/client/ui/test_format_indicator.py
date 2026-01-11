#!/usr/bin/env python3
"""Unit tests for format_indicator function."""

from pathlib import Path

import pytest

from platyplaty.ui.directory_types import EntryType
from platyplaty.ui.indicators import format_indicator


class TestFormatIndicatorDirectory:
    """Tests for format_indicator with DIRECTORY type."""

    def test_directory_returns_count(self, tmp_path: Path) -> None:
        """Directory indicator is the count of filtered contents."""
        (tmp_path / "preset.milk").write_text("content")
        (tmp_path / "subdir").mkdir()
        result = format_indicator(EntryType.DIRECTORY, tmp_path)
        assert result == "2"

    def test_empty_directory_returns_zero(self, tmp_path: Path) -> None:
        """Empty directory returns '0'."""
        result = format_indicator(EntryType.DIRECTORY, tmp_path)
        assert result == "0"


class TestFormatIndicatorFile:
    """Tests for format_indicator with FILE type."""

    def test_file_returns_formatted_size(self, tmp_path: Path) -> None:
        """File indicator is the formatted file size."""
        test_file = tmp_path / "test.milk"
        test_file.write_text("x" * 512)
        result = format_indicator(EntryType.FILE, test_file)
        assert result == "512 B"


class TestFormatIndicatorSymlinkToDirectory:
    """Tests for format_indicator with SYMLINK_TO_DIRECTORY type."""

    def test_symlink_to_dir_returns_arrow_count(self, tmp_path: Path) -> None:
        """Symlink to directory returns '-> COUNT'."""
        target = tmp_path / "target_dir"
        target.mkdir()
        (target / "file.milk").write_text("content")
        link = tmp_path / "link"
        link.symlink_to(target)
        result = format_indicator(EntryType.SYMLINK_TO_DIRECTORY, link)
        assert result == "-> 1"


class TestFormatIndicatorSymlinkToFile:
    """Tests for format_indicator with SYMLINK_TO_FILE type."""

    def test_symlink_to_file_returns_arrow_size(self, tmp_path: Path) -> None:
        """Symlink to file returns '-> SIZE'."""
        target = tmp_path / "target.milk"
        target.write_text("x" * 2048)
        link = tmp_path / "link.milk"
        link.symlink_to(target)
        result = format_indicator(EntryType.SYMLINK_TO_FILE, link)
        assert result == "-> 2 K"


class TestFormatIndicatorBrokenSymlink:
    """Tests for format_indicator with BROKEN_SYMLINK type."""

    def test_broken_symlink_returns_arrow_size(self, tmp_path: Path) -> None:
        """Broken symlink returns '-> SIZE' of symlink file itself."""
        link = tmp_path / "broken.milk"
        link.symlink_to(tmp_path / "nonexistent")
        result = format_indicator(EntryType.BROKEN_SYMLINK, link)
        # Symlink size is the length of target path string
        assert result.startswith("-> ")
        assert " B" in result
