#!/usr/bin/env python3
"""Tests for pane rendering with non-selected items.

This module tests render_pane_line() behavior for items that are not
currently selected, verifying normal (non-inverted) colors are applied.
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


def make_listing(entries: list[DirectoryEntry]) -> DirectoryListing:
    """Create a DirectoryListing from entries."""
    return DirectoryListing(
        entries=entries,
        was_empty=len(entries) == 0,
        had_filtered_entries=False,
        permission_denied=False,
    )


class TestRenderNonSelectedItems:
    """Tests for rendering non-selected items with normal colors."""

    def test_non_selected_directory_has_normal_colors(self) -> None:
        """Non-selected directory should have blue on black."""
        entries = [
            DirectoryEntry("first", EntryType.DIRECTORY, Path("/dummy")),
            DirectoryEntry("second", EntryType.DIRECTORY, Path("/dummy")),
        ]
        listing = make_listing(entries)
        # Select index 1, render index 0 (non-selected)
        segments = render_pane_line(listing, 0, 20, False, selected_index=1)
        assert any(
            s.style.color.name == DIRECTORY_COLOR
            for s in segments if s.style and s.style.color
        )
        assert any(
            s.style.bgcolor.name == BACKGROUND_COLOR
            for s in segments if s.style and s.style.bgcolor
        )

    def test_non_selected_file_has_normal_colors(self) -> None:
        """Non-selected file should have white on black."""
        entries = [
            DirectoryEntry("first.milk", EntryType.FILE, Path("/dummy")),
            DirectoryEntry("second.milk", EntryType.FILE, Path("/dummy")),
        ]
        listing = make_listing(entries)
        segments = render_pane_line(listing, 0, 20, False, selected_index=1)
        assert any(
            s.style.color.name == FILE_COLOR
            for s in segments if s.style and s.style.color
        )
        assert any(
            s.style.bgcolor.name == BACKGROUND_COLOR
            for s in segments if s.style and s.style.bgcolor
        )
