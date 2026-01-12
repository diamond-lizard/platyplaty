#!/usr/bin/env python3
"""Tests for get_right_pane_content - None entry and broken symlinks."""

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
