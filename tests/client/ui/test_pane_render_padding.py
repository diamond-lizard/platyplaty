#!/usr/bin/env python3
"""Tests for selection highlight padding.

This module tests that selected entries have correct padding spaces
with inverted style applied.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

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


def _all_segments_have_bgcolor(segments, expected: str) -> bool:
    """Check if all segments with bgcolor have the expected color."""
    return all(
        s.style.bgcolor.name == expected
        for s in segments if s.style and s.style.bgcolor
    )


def _all_segments_have_color(segments, expected: str) -> bool:
    """Check if all segments with color have the expected color."""
    return all(
        s.style.color.name == expected
        for s in segments if s.style and s.style.color
    )


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
        assert _all_segments_have_bgcolor(segments, "white")
        assert _all_segments_have_color(segments, "black")
