#!/usr/bin/env python3
"""Unit tests for truncate_entry function (TASK-09300)."""

import pytest

from platyplaty.ui.directory_types import EntryType
from platyplaty.ui.truncation_entry import truncate_entry


class TestTruncateEntryNoIndicatorDirectory:
    """Tests for DIRECTORY with show_indicator=False."""

    def test_directory_fits(self) -> None:
        """Directory name fits, returns as-is."""
        result = truncate_entry("presets", EntryType.DIRECTORY, 42, 20, False)
        assert result == "presets"

    def test_directory_truncates(self) -> None:
        """Directory name truncated with tilde (simple truncation)."""
        result = truncate_entry("very-long-dir", EntryType.DIRECTORY, 42, 8, False)
        assert result == "very-lo~"


class TestTruncateEntryNoIndicatorFile:
    """Tests for FILE with show_indicator=False."""

    def test_file_with_extension_fits(self) -> None:
        """File with extension fits, returns as-is."""
        result = truncate_entry("preset.milk", EntryType.FILE, "1.5 K", 20, False)
        assert result == "preset.milk"

    def test_file_with_extension_truncates(self) -> None:
        """File with extension uses multi-stage truncation."""
        result = truncate_entry("very-long-preset.milk", EntryType.FILE, "1.5 K", 12, False)
        # Base is truncated, extension preserved: "very-l~.milk" (12 chars)
        assert result == "very-l~.milk"

    def test_file_without_extension_truncates(self) -> None:
        """File without extension uses simple truncation."""
        result = truncate_entry("Makefile", EntryType.FILE, "512 B", 6, False)
        assert result == "Makef~"


class TestTruncateEntryNoIndicatorSymlinkToDir:
    """Tests for SYMLINK_TO_DIRECTORY with show_indicator=False."""

    def test_symlink_to_dir_fits(self) -> None:
        """Symlink to directory name fits, returns as-is."""
        result = truncate_entry("favorites", EntryType.SYMLINK_TO_DIRECTORY, "-> 42", 20, False)
        assert result == "favorites"

    def test_symlink_to_dir_truncates(self) -> None:
        """Symlink to directory uses simple truncation (like directory)."""
        result = truncate_entry("my-favorites", EntryType.SYMLINK_TO_DIRECTORY, "-> 42", 8, False)
        assert result == "my-favo~"


class TestTruncateEntryNoIndicatorSymlinkToFile:
    """Tests for SYMLINK_TO_FILE with show_indicator=False."""

    def test_symlink_to_file_fits(self) -> None:
        """Symlink to file name fits, returns as-is."""
        result = truncate_entry("link.milk", EntryType.SYMLINK_TO_FILE, "-> 1.5 K", 20, False)
        assert result == "link.milk"

    def test_symlink_to_file_truncates(self) -> None:
        """Symlink to file uses file truncation rules (preserves extension)."""
        result = truncate_entry("very-long-link.milk", EntryType.SYMLINK_TO_FILE, "-> 1.5 K", 12, False)
        # Uses file truncation: base truncated, extension preserved
        assert result == "very-l~.milk"


class TestTruncateEntryNoIndicatorBrokenSymlink:
    """Tests for BROKEN_SYMLINK with show_indicator=False."""

    def test_broken_symlink_fits(self) -> None:
        """Broken symlink name fits, returns as-is."""
        result = truncate_entry("dead.milk", EntryType.BROKEN_SYMLINK, "-> 15 B", 20, False)
        assert result == "dead.milk"

    def test_broken_symlink_with_ext_truncates(self) -> None:
        """Broken symlink with extension uses file truncation rules."""
        result = truncate_entry("very-long-dead.milk", EntryType.BROKEN_SYMLINK, "-> 15 B", 12, False)
        # Uses file truncation: base truncated, extension preserved
        assert result == "very-l~.milk"

    def test_broken_symlink_no_ext_truncates(self) -> None:
        """Broken symlink without extension uses simple file truncation."""
        result = truncate_entry("deadlink", EntryType.BROKEN_SYMLINK, "-> 15 B", 6, False)
        assert result == "deadl~"
