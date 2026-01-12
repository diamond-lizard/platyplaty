#!/usr/bin/env python3
"""Tests for get_right_pane_content - directory content types."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.directory_types import DirectoryEntry, EntryType
from platyplaty.ui.file_browser_preview import get_right_pane_content
from platyplaty.ui.file_browser_types import (
    RightPaneDirectory,
    RightPaneEmpty,
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
