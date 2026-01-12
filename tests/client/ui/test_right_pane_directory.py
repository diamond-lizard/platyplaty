#!/usr/bin/env python3
"""Tests for get_right_pane_content - directory content types."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.directory_types import DirectoryEntry, DirectoryListing, EntryType
from platyplaty.ui.file_browser_preview import get_right_pane_content
from platyplaty.ui.file_browser_types import (
    RightPaneDirectory,
    RightPaneEmpty,
    RightPaneNoMilk,
)
from platyplaty.ui.file_browser_right_pane_render import render_right_pane_line


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


class TestSortedFilteredEntries:
    """Tests for directory preview returning sorted, filtered entries (TASK-1610)."""

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


class TestMaxLinesLimit:
    """Tests for directory preview limited to max lines (TASK-1620)."""

    def test_render_only_entries_within_pane_height(self) -> None:
        """Rendering only produces output for lines within pane height."""
        # Create a directory listing with 5 entries
        entries = [
            DirectoryEntry("dir1", EntryType.DIRECTORY, Path("/test/dir1")),
            DirectoryEntry("dir2", EntryType.DIRECTORY, Path("/test/dir2")),
            DirectoryEntry("file1.milk", EntryType.FILE, Path("/test/file1.milk")),
            DirectoryEntry("file2.milk", EntryType.FILE, Path("/test/file2.milk")),
            DirectoryEntry("file3.milk", EntryType.FILE, Path("/test/file3.milk")),
        ]
        listing = DirectoryListing(
            entries=entries,
            was_empty=False,
            had_filtered_entries=False,
            permission_denied=False,
        )
        content = RightPaneDirectory(listing)
        width = 20
        # Simulate pane height of 3 - only first 3 entries visible
        pane_height = 3
        results = []
        for y in range(pane_height):
            segments = render_right_pane_line(content, y, width)
            line_text = "".join(seg.text for seg in segments)
            results.append(line_text.strip())
        # Should show dir1, dir2, file1.milk (first 3 entries)
        assert "dir1" in results[0]
        assert "dir2" in results[1]
        assert "file1" in results[2]
        # file2 and file3 are beyond pane height, not rendered

    def test_scroll_offset_limits_visible_entries(self) -> None:
        """Scroll offset adjusts which entries are visible."""
        entries = [
            DirectoryEntry("entry0", EntryType.DIRECTORY, Path("/test/entry0")),
            DirectoryEntry("entry1", EntryType.DIRECTORY, Path("/test/entry1")),
            DirectoryEntry("entry2.milk", EntryType.FILE, Path("/test/entry2.milk")),
            DirectoryEntry("entry3.milk", EntryType.FILE, Path("/test/entry3.milk")),
            DirectoryEntry("entry4.milk", EntryType.FILE, Path("/test/entry4.milk")),
        ]
        listing = DirectoryListing(
            entries=entries,
            was_empty=False,
            had_filtered_entries=False,
            permission_denied=False,
        )
        content = RightPaneDirectory(listing)
        width = 20
        # With scroll_offset=2, we start from entry2
        scroll_offset = 2
        pane_height = 2
        results = []
        for y in range(pane_height):
            segments = render_right_pane_line(
                content, y, width, scroll_offset=scroll_offset
            )
            line_text = "".join(seg.text for seg in segments)
            results.append(line_text.strip())
        # Should show entry2 and entry3 (indices 2 and 3)
        assert "entry2" in results[0]
        assert "entry3" in results[1]
