#!/usr/bin/env python3
"""Tests for gap segment styling in file_browser_render.

This module tests that render_line() applies correct black background
to the gap characters between panes.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.colors import BACKGROUND_COLOR
from platyplaty.ui.directory_types import DirectoryEntry, DirectoryListing, EntryType
from platyplaty.ui.file_browser_render import render_line
from platyplaty.ui.file_browser_types import RightPaneDirectory
from platyplaty.ui.layout import calculate_standard_widths


def _make_listing(entry: DirectoryEntry) -> DirectoryListing:
    """Create a simple listing with one entry."""
    return DirectoryListing(
        entries=[entry],
        was_empty=False,
        had_filtered_entries=False,
        permission_denied=False,
    )

def _make_mock_browser(width: int = 80) -> MagicMock:
    """Create a mock browser with minimal attributes for render_line testing."""
    entry = DirectoryEntry(name="test.milk", entry_type=EntryType.FILE, path=Path("/dummy"))
    listing = _make_listing(entry)
    right_content = RightPaneDirectory(listing=listing)
    browser = MagicMock()
    browser.size.width = width
    browser._left_listing = listing
    browser._middle_listing = listing
    browser._right_content = right_content
    browser._left_scroll_offset = 0
    browser._middle_scroll_offset = 0
    browser._right_scroll_offset = 0
    browser.selected_index = 0
    browser._right_selected_index = 0
    browser.current_dir = Path("/test")
    return browser

def _find_gap_segments(strip, width: int):
    """Find gap segments between panes using positional detection.

    Gap segments occur at specific positions based on pane layout:
    - After left pane: at position left_width
    - After middle pane: at position left_width + 1 + middle_width

    This is more robust than filtering by segment properties, since
    entry padding segments also have black background.
    """
    pane_widths = calculate_standard_widths(width)
    gap_positions = set()
    if pane_widths.left > 0:
        gap_positions.add(pane_widths.left)
        gap_positions.add(pane_widths.left + 1 + pane_widths.middle)
    else:
        gap_positions.add(pane_widths.middle)
    gaps = []
    pos = 0
    for segment in strip:
        if pos in gap_positions:
            gaps.append(segment)
        pos += len(segment.text)
    return gaps

class TestRenderLineGapBackgrounds:
    """Tests for gap segment background styling in render_line()."""

    def test_gap_segments_have_black_background(self) -> None:
        """Gap segments between panes should have black background."""
        browser = _make_mock_browser(width=80)
        strip = render_line(browser, y=1)
        gaps = _find_gap_segments(strip, width=80)
        # Should have 2 gaps: after left pane and after middle pane
        assert len(gaps) == 2
        for gap in gaps:
            assert gap.style is not None
            assert gap.style.bgcolor is not None
            assert gap.style.bgcolor.name == BACKGROUND_COLOR


    def test_single_gap_when_left_pane_collapsed(self) -> None:
        """When left pane collapses at narrow width, only one gap remains."""
        # At width 7, left pane width = int(7 * 1/8) = 0, so left pane disappears
        browser = _make_mock_browser(width=7)
        strip = render_line(browser, y=1)
        gaps = _find_gap_segments(strip, width=7)
        # Should have only 1 gap: after middle pane (no left pane)
        assert len(gaps) == 1
        assert gaps[0].style is not None
        assert gaps[0].style.bgcolor is not None
        assert gaps[0].style.bgcolor.name == BACKGROUND_COLOR
