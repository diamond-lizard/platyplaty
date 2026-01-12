#!/usr/bin/env python3
"""Tests for get_right_pane_content - file content types."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.directory_types import DirectoryEntry, EntryType
from platyplaty.ui.file_browser_preview import get_right_pane_content
from platyplaty.ui.file_browser_types import (
    RightPaneBinaryFile,
    RightPaneFilePreview,
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
