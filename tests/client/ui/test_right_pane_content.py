#!/usr/bin/env python3
"""Tests for get_right_pane_content function.

This module tests the right pane content determination logic to verify
correct content types are returned for each entry type.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.directory_entry import get_entry_type
from platyplaty.ui.directory_types import DirectoryEntry, EntryType
from platyplaty.ui.file_browser_preview import get_right_pane_content
from platyplaty.ui.file_browser_types import (
    RightPaneBinaryFile,
    RightPaneDirectory,
    RightPaneEmpty,
    RightPaneFilePreview,
    RightPaneNoMilk,
)


def make_entry(name: str, entry_type: EntryType, path: Path) -> DirectoryEntry:
    """Create a DirectoryEntry for testing."""
    return DirectoryEntry(name=name, entry_type=entry_type, path=path)


def make_browser(current_dir: Path) -> MagicMock:
    """Create a mock FileBrowser with the given current directory."""
    browser = MagicMock()
    browser.current_dir = current_dir
    browser._nav_state = MagicMock()
    browser._nav_state.get_selected_name_for_directory.return_value = None
    return browser


class TestNoneEntry:
    """Tests for None selected entry (TASK-0810)."""

    def test_none_entry_returns_none(self, tmp_path: Path) -> None:
        """When selected_entry is None, return None."""
        browser = make_browser(tmp_path)
        result = get_right_pane_content(browser, None)
        assert result is None


class TestBrokenSymlink:
    """Tests for broken symlinks (TASK-0810, TASK-0890)."""

    def test_broken_symlink_returns_none(self, tmp_path: Path) -> None:
        """Broken symlink triggers collapsed state (returns None)."""
        target = tmp_path / "nonexistent"
        link = tmp_path / "broken_link.milk"
        link.symlink_to(target)
        browser = make_browser(tmp_path)
        entry = make_entry("broken_link.milk", EntryType.BROKEN_SYMLINK, link)
        result = get_right_pane_content(browser, entry)
        assert result is None


class TestDirectoryContent:
    """Tests for directory content (TASK-0810)."""

    def test_directory_returns_right_pane_directory(
        self, tmp_path: Path
    ) -> None:
        """Regular directory with content returns RightPaneDirectory."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "file.milk").write_text("content")
        browser = make_browser(tmp_path)
        entry = make_entry("subdir", EntryType.DIRECTORY, subdir)
        result = get_right_pane_content(browser, entry)
        assert isinstance(result, RightPaneDirectory)

    def test_symlink_to_directory_returns_right_pane_directory(
        self, tmp_path: Path
    ) -> None:
        """Symlink to directory with content returns RightPaneDirectory."""
        target = tmp_path / "target"
        target.mkdir()
        (target / "file.milk").write_text("content")
        link = tmp_path / "link"
        link.symlink_to(target)
        browser = make_browser(tmp_path)
        entry = make_entry("link", EntryType.SYMLINK_TO_DIRECTORY, link)
        result = get_right_pane_content(browser, entry)
        assert isinstance(result, RightPaneDirectory)


class TestFileContent:
    """Tests for file content (TASK-0810)."""

    def test_file_returns_right_pane_file_preview(self, tmp_path: Path) -> None:
        """Regular file with content returns RightPaneFilePreview."""
        test_file = tmp_path / "test.milk"
        test_file.write_text("preset content")
        browser = make_browser(tmp_path)
        entry = make_entry("test.milk", EntryType.FILE, test_file)
        result = get_right_pane_content(browser, entry)
        assert isinstance(result, RightPaneFilePreview)

    def test_symlink_to_file_returns_right_pane_file_preview(
        self, tmp_path: Path
    ) -> None:
        """Symlink to file with content returns RightPaneFilePreview."""
        target = tmp_path / "target.milk"
        target.write_text("content")
        link = tmp_path / "link.milk"
        link.symlink_to(target)
        browser = make_browser(tmp_path)
        entry = make_entry("link.milk", EntryType.SYMLINK_TO_FILE, link)
        result = get_right_pane_content(browser, entry)
        assert isinstance(result, RightPaneFilePreview)


class TestEmptyDirectory:
    """Tests for empty directory handling (TASK-0820)."""

    def test_truly_empty_directory_returns_right_pane_empty(
        self, tmp_path: Path
    ) -> None:
        """Truly empty directory returns RightPaneEmpty."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        browser = make_browser(tmp_path)
        entry = make_entry("empty", EntryType.DIRECTORY, empty_dir)
        result = get_right_pane_content(browser, entry)
        assert isinstance(result, RightPaneEmpty)

    def test_filtered_empty_directory_returns_right_pane_no_milk(
        self, tmp_path: Path
    ) -> None:
        """Directory with non-.milk files only returns RightPaneNoMilk."""
        filtered_dir = tmp_path / "filtered"
        filtered_dir.mkdir()
        (filtered_dir / "readme.txt").write_text("not a milk file")
        (filtered_dir / "other.py").write_text("also not milk")
        browser = make_browser(tmp_path)
        entry = make_entry("filtered", EntryType.DIRECTORY, filtered_dir)
        result = get_right_pane_content(browser, entry)
        assert isinstance(result, RightPaneNoMilk)


class TestBinaryFile:
    """Tests for binary file handling (TASK-0830)."""

    def test_binary_file_returns_right_pane_binary_file(
        self, tmp_path: Path
    ) -> None:
        """Binary file (non-UTF-8) returns RightPaneBinaryFile."""
        binary_file = tmp_path / "binary.milk"
        binary_file.write_bytes(b"\x80\x81\x82\xff\xfe")
        browser = make_browser(tmp_path)
        entry = make_entry("binary.milk", EntryType.FILE, binary_file)
        result = get_right_pane_content(browser, entry)
        assert isinstance(result, RightPaneBinaryFile)


class TestEmptyFile:
    """Tests for empty file handling (TASK-0840)."""

    def test_empty_file_returns_none(self, tmp_path: Path) -> None:
        """Empty file (0 bytes) returns None (collapsed state)."""
        empty_file = tmp_path / "empty.milk"
        empty_file.write_text("")
        browser = make_browser(tmp_path)
        entry = make_entry("empty.milk", EntryType.FILE, empty_file)
        result = get_right_pane_content(browser, entry)
        assert result is None


class TestLargeFile:
    """Tests for large file handling (TASK-0850)."""

    def test_large_file_returns_none(self, tmp_path: Path) -> None:
        """File larger than 10 MB returns None (collapsed state)."""
        large_file = tmp_path / "large.milk"
        # Create a file just over 10 MB
        large_file.write_bytes(b"x" * (10 * 1024 * 1024 + 1))
        browser = make_browser(tmp_path)
        entry = make_entry("large.milk", EntryType.FILE, large_file)
        result = get_right_pane_content(browser, entry)
        assert result is None


class TestPermissionDenied:
    """Tests for permission denied handling (TASK-0860)."""

    def test_permission_denied_file_returns_none(self, tmp_path: Path) -> None:
        """File with no read permission returns None (collapsed state)."""
        protected_file = tmp_path / "protected.milk"
        protected_file.write_text("content")
        protected_file.chmod(0o000)
        try:
            browser = make_browser(tmp_path)
            entry = make_entry("protected.milk", EntryType.FILE, protected_file)
            result = get_right_pane_content(browser, entry)
            assert result is None
        finally:
            protected_file.chmod(0o644)


class TestFileVanishes:
    """Tests for file vanishing after listing (TASK-0870)."""

    def test_file_vanishes_returns_none(self, tmp_path: Path) -> None:
        """File that doesn't exist returns None (collapsed state)."""
        missing_file = tmp_path / "missing.milk"
        # Create entry for a file that doesn't exist
        browser = make_browser(tmp_path)
        entry = make_entry("missing.milk", EntryType.FILE, missing_file)
        result = get_right_pane_content(browser, entry)
        assert result is None


class TestStatFailure:
    """Tests for stat() failure handling (TASK-0880)."""

    def test_stat_failure_returns_none(self, tmp_path: Path) -> None:
        """File where stat() fails returns None (collapsed state).

        This is effectively the same as file vanishing - OSError on stat.
        """
        missing_file = tmp_path / "nonexistent.milk"
        browser = make_browser(tmp_path)
        entry = make_entry("nonexistent.milk", EntryType.FILE, missing_file)
        result = get_right_pane_content(browser, entry)
        assert result is None
