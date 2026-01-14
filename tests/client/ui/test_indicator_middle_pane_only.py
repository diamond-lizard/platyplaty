#!/usr/bin/env python3
"""Integration tests for indicator display in middle pane only.

This module verifies that indicators (directory counts, file sizes)
appear only in the middle pane, not in left or right panes.
"""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.directory_types import DirectoryEntry, DirectoryListing, EntryType
from platyplaty.ui.file_browser_pane_render import render_pane_line


def _make_listing(entry: DirectoryEntry) -> DirectoryListing:
    """Create a simple listing with one entry."""
    return DirectoryListing(
        entries=[entry],
        was_empty=False,
        had_filtered_entries=False,
        permission_denied=False,
    )


class TestMiddlePaneIndicators:
    """Tests verifying indicators appear only in middle pane."""

    @patch("platyplaty.ui.file_browser_entry_render.count_directory_contents", return_value=42)
    def test_middle_pane_shows_indicator(self, mock_count) -> None:
        """Middle pane with show_indicators=True shows indicator."""
        entry = DirectoryEntry(
            name="mydir", entry_type=EntryType.DIRECTORY, path=Path("/test")
        )
        result = render_pane_line(
            _make_listing(entry), y=0, width=30, is_left_pane=False,
            show_indicators=True
        )
        # Content segment is the middle one (after left padding)
        content = "".join(seg.text for seg in result)
        assert "42" in content, f"Indicator '42' not found in content: {content!r}"

    @patch("platyplaty.ui.file_browser_entry_render.count_directory_contents", return_value=42)
    def test_left_pane_no_indicator(self, mock_count) -> None:
        """Left pane (show_indicators=False) should not show indicator."""
        entry = DirectoryEntry(
            name="mydir", entry_type=EntryType.DIRECTORY, path=Path("/test")
        )
        result = render_pane_line(
            _make_listing(entry), y=0, width=30, is_left_pane=True,
            show_indicators=False
        )
        content = "".join(seg.text for seg in result)
        assert "42" not in content, f"Indicator '42' found in left pane: {content!r}"

    @patch("platyplaty.ui.file_browser_entry_render.count_directory_contents", return_value=42)
    def test_default_show_indicators_is_true(self, mock_count) -> None:
        """Default show_indicators=True does show indicator."""
        entry = DirectoryEntry(
            name="mydir", entry_type=EntryType.DIRECTORY, path=Path("/test")
        )
        result = render_pane_line(
            _make_listing(entry), y=0, width=30, is_left_pane=False
        )
        content = "".join(seg.text for seg in result)
        assert "42" in content, f"Indicator '42' not found with default: {content!r}"
