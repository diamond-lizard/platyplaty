#!/usr/bin/env python3
"""Tests for get_right_pane_content - edge cases."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.directory_types import DirectoryEntry, EntryType
from platyplaty.ui.file_browser_preview import get_right_pane_content


def make_entry(name: str, entry_type: EntryType, path: Path) -> DirectoryEntry:
    """Create a DirectoryEntry for testing."""
    return DirectoryEntry(name=name, entry_type=entry_type, path=path)


def make_browser(current_dir: Path) -> MagicMock:
    """Create a mock FileBrowser with the given current directory."""
    browser = MagicMock()
    browser.current_dir = current_dir
    browser._nav_state = MagicMock()
    browser._nav_state.get_selected_name_for_directory.return_value = None
    browser.size = MagicMock()
    browser.size.height = 32
    return browser


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
        browser = make_browser(tmp_path)
        entry = make_entry("missing.milk", EntryType.FILE, missing_file)
        result = get_right_pane_content(browser, entry)
        assert result is None


class TestStatFailure:
    """Tests for stat() failure handling (TASK-0880)."""

    def test_stat_failure_returns_none(self, tmp_path: Path) -> None:
        """File where stat() fails returns None (collapsed state)."""
        missing_file = tmp_path / "nonexistent.milk"
        browser = make_browser(tmp_path)
        entry = make_entry("nonexistent.milk", EntryType.FILE, missing_file)
        result = get_right_pane_content(browser, entry)
        assert result is None
