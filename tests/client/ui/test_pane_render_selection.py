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
    SYMLINK_COLOR,
)
from platyplaty.ui.directory_types import DirectoryEntry, DirectoryListing, EntryType
from platyplaty.ui.file_browser_pane_render import render_pane_line


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


class TestRenderNonSelectedItems:
    """Tests for rendering non-selected items with normal colors."""

    def test_non_selected_directory_has_normal_colors(self) -> None:
        """Non-selected directory should have blue on black."""
        entries = [
            DirectoryEntry("first", EntryType.DIRECTORY),
            DirectoryEntry("second", EntryType.DIRECTORY),
        ]
        listing = make_listing(entries)
        # Select index 1, render index 0 (non-selected)
        segments = render_pane_line(listing, 0, 20, False, selected_index=1)
        assert any(s.style.color.name == DIRECTORY_COLOR for s in segments if s.style and s.style.color)
        assert any(s.style.bgcolor.name == BACKGROUND_COLOR for s in segments if s.style and s.style.bgcolor)

    def test_non_selected_file_has_normal_colors(self) -> None:
        """Non-selected file should have white on black."""
        entries = [
            DirectoryEntry("first.milk", EntryType.FILE),
            DirectoryEntry("second.milk", EntryType.FILE),
        ]
        listing = make_listing(entries)
        segments = render_pane_line(listing, 0, 20, False, selected_index=1)
        assert any(s.style.color.name == FILE_COLOR for s in segments if s.style and s.style.color)
        assert any(s.style.bgcolor.name == BACKGROUND_COLOR for s in segments if s.style and s.style.bgcolor)


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
        # Should not have black foreground (which indicates selection)
        for seg in segments:
            if seg.style and seg.style.color:
                assert seg.style.color.name != "black"


class TestSelectionPadding:
    """Tests for selection highlight padding."""

    def test_selected_entry_has_left_padding(self) -> None:
        """Selected entry should include left padding space."""
        entries = [DirectoryEntry("test", EntryType.FILE)]
        listing = make_listing(entries)
        # Width 20, name "test" is 4 chars, should have room for padding
        segments = render_pane_line(listing, 0, 20, False, selected_index=0)
        # First segment should be a space (left padding)
        assert segments[0].text == " "

    def test_selected_entry_has_right_padding(self) -> None:
        """Selected entry should include right padding space."""
        entries = [DirectoryEntry("test", EntryType.FILE)]
        listing = make_listing(entries)
        segments = render_pane_line(listing, 0, 20, False, selected_index=0)
        # Last segment should be a space (right padding)
        assert segments[-1].text == " "

    def test_padding_has_inverted_style(self) -> None:
        """Padding spaces should have the same inverted style as content."""
        entries = [DirectoryEntry("test.milk", EntryType.FILE)]
        listing = make_listing(entries)
        segments = render_pane_line(listing, 0, 20, False, selected_index=0)
        # All segments should have black foreground on white background
        for seg in segments:
            if seg.style and seg.style.bgcolor:
                assert seg.style.bgcolor.name == "white"
            if seg.style and seg.style.color:
                assert seg.style.color.name == "black"
