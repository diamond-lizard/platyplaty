#!/usr/bin/env python3
"""Tests for directory preview sorting and filtering (TASK-1610)."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.directory_types import DirectoryEntry, EntryType
from platyplaty.ui.file_browser_preview import get_right_pane_content
from platyplaty.ui.file_browser_types import RightPaneDirectory


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


class TestSortedFilteredEntries:
    """Tests for directory preview returning sorted, filtered entries."""

    def test_directory_entries_are_sorted_directories_first(
        self, tmp_path: Path
    ) -> None:
        """Directories appear before files, case-insensitive sort."""
        subdir = tmp_path / "testdir"
        subdir.mkdir()
        # Create files and directories in non-sorted order
        (subdir / "zebra.milk").write_text("content")
        (subdir / "alpha").mkdir()
        (subdir / "beta.milk").write_text("content")
        (subdir / "Beta").mkdir()  # Different case
        browser = make_browser(tmp_path)
        entry = make_entry("testdir", EntryType.DIRECTORY, subdir)
        result = get_right_pane_content(browser, entry)
        assert isinstance(result, RightPaneDirectory)
        names = [e.name for e in result.listing.entries]
        # Directories first (alpha, Beta), then files (beta.milk, zebra.milk)
        assert names == ["alpha", "Beta", "beta.milk", "zebra.milk"]

    def test_directory_entries_are_filtered(
        self, tmp_path: Path
    ) -> None:
        """Only .milk files and directories are included."""
        subdir = tmp_path / "testdir"
        subdir.mkdir()
        (subdir / "preset.milk").write_text("content")
        (subdir / "readme.txt").write_text("filtered out")
        (subdir / "script.py").write_text("filtered out")
        (subdir / "subdir").mkdir()
        browser = make_browser(tmp_path)
        entry = make_entry("testdir", EntryType.DIRECTORY, subdir)
        result = get_right_pane_content(browser, entry)
        assert isinstance(result, RightPaneDirectory)
        names = [e.name for e in result.listing.entries]
        # Only the directory and .milk file
        assert names == ["subdir", "preset.milk"]
