#!/usr/bin/env python3
"""Tests for directory preview max lines limit (TASK-1620)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.directory_types import DirectoryEntry, DirectoryListing, EntryType
from platyplaty.ui.file_browser_types import RightPaneDirectory
from platyplaty.ui.file_browser_right_pane_render import render_right_pane_line


def render_lines(content, pane_height, width, scroll_offset=0):
    """Render multiple lines and return stripped text for each."""
    results = []
    for y in range(pane_height):
        segments = render_right_pane_line(content, y, width, scroll_offset)
        line_text = "".join(seg.text for seg in segments)
        results.append(line_text.strip())
    return results


def make_test_listing(names_and_types):
    """Create a DirectoryListing from name/type pairs."""
    entries = [
        DirectoryEntry(name, etype, Path(f"/test/{name}"))
        for name, etype in names_and_types
    ]
    return DirectoryListing(
        entries=entries,
        was_empty=False,
        had_filtered_entries=False,
        permission_denied=False,
    )


class TestMaxLinesLimit:
    """Tests for directory preview limited to max lines."""

    def test_render_only_entries_within_pane_height(self) -> None:
        """Rendering only produces output for lines within pane height."""
        items = [
            ("dir1", EntryType.DIRECTORY),
            ("dir2", EntryType.DIRECTORY),
            ("file1.milk", EntryType.FILE),
            ("file2.milk", EntryType.FILE),
            ("file3.milk", EntryType.FILE),
        ]
        listing = make_test_listing(items)
        content = RightPaneDirectory(listing)
        # Simulate pane height of 3 - only first 3 entries visible
        results = render_lines(content, pane_height=3, width=20)
        # Should show dir1, dir2, file1.milk (first 3 entries)
        assert "dir1" in results[0]
        assert "dir2" in results[1]
        assert "file1" in results[2]

    def test_scroll_offset_limits_visible_entries(self) -> None:
        """Scroll offset adjusts which entries are visible."""
        items = [
            ("entry0", EntryType.DIRECTORY),
            ("entry1", EntryType.DIRECTORY),
            ("entry2.milk", EntryType.FILE),
            ("entry3.milk", EntryType.FILE),
            ("entry4.milk", EntryType.FILE),
        ]
        listing = make_test_listing(items)
        content = RightPaneDirectory(listing)
        # With scroll_offset=2, we start from entry2
        results = render_lines(content, pane_height=2, width=20, scroll_offset=2)
        # Should show entry2 and entry3 (indices 2 and 3)
        assert "entry2" in results[0]
        assert "entry3" in results[1]
