#!/usr/bin/env python3
"""Tests for pane rendering with selection highlighting.

This module tests render_pane_line() behavior with selected_index parameter
for correctly applying inverted colors to selected items.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.colors import (
    BACKGROUND_COLOR,
    DIRECTORY_COLOR,
    FILE_COLOR,
)
from platyplaty.ui.directory_types import DirectoryEntry, DirectoryListing, EntryType
from platyplaty.ui.file_browser_pane_render import render_pane_line

def _no_segment_has_black_foreground(segments) -> bool:
    """Check that no segment has black foreground (selection indicator)."""
    return all(
        s.style.color.name != "black"
        for s in segments if s.style and s.style.color
    )


def make_listing(entries: list[DirectoryEntry]) -> DirectoryListing:
    """Create a DirectoryListing from entries."""
    return DirectoryListing(
        entries=entries,
        was_empty=len(entries) == 0,
        had_filtered_entries=False,
        permission_denied=False,
    )


class TestRenderSelectedItem:
    """Tests for rendering selected items with inverted colors."""

    def test_selected_directory_has_inverted_colors(self) -> None:
        """Selected directory should have black on blue."""
        entries = [DirectoryEntry("subdir", EntryType.DIRECTORY)]
        listing = make_listing(entries)
        segments = render_pane_line(listing, 0, 20, False, selected_index=0)
        # Check that segment has inverted colors
        assert any(s.style.bgcolor.name == "blue" for s in segments if s.style and s.style.bgcolor)
        assert any(s.style.color.name == "black" for s in segments if s.style and s.style.color)

    def test_selected_file_has_inverted_colors(self) -> None:
        """Selected file should have black on white."""
        entries = [DirectoryEntry("test.milk", EntryType.FILE)]
        listing = make_listing(entries)
        segments = render_pane_line(listing, 0, 20, False, selected_index=0)
        assert any(s.style.bgcolor.name == "white" for s in segments if s.style and s.style.bgcolor)
        assert any(s.style.color.name == "black" for s in segments if s.style and s.style.color)

    def test_selected_symlink_has_inverted_colors(self) -> None:
        """Selected symlink should have black on cyan."""
        entries = [DirectoryEntry("link", EntryType.SYMLINK_TO_DIRECTORY)]
        listing = make_listing(entries)
        segments = render_pane_line(listing, 0, 20, False, selected_index=0)
        assert any(s.style.bgcolor.name == "cyan" for s in segments if s.style and s.style.bgcolor)
        assert any(s.style.color.name == "black" for s in segments if s.style and s.style.color)


class TestRenderWithNoSelection:
    """Tests for rendering with selected_index=None."""

    def test_none_selection_renders_normal_colors(self) -> None:
        """With selected_index=None, all items have normal colors."""
        entries = [DirectoryEntry("subdir", EntryType.DIRECTORY)]
        listing = make_listing(entries)
        segments = render_pane_line(listing, 0, 20, False, selected_index=None)
        assert any(s.style.color.name == DIRECTORY_COLOR for s in segments if s.style and s.style.color)
        assert any(s.style.bgcolor.name == BACKGROUND_COLOR for s in segments if s.style and s.style.bgcolor)

    def test_none_selection_no_inverted_colors(self) -> None:
        """With selected_index=None, no item should have inverted colors."""
        entries = [DirectoryEntry("test.milk", EntryType.FILE)]
        listing = make_listing(entries)
        segments = render_pane_line(listing, 0, 20, False, selected_index=None)
        assert _no_segment_has_black_foreground(segments)

