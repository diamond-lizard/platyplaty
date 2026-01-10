#!/usr/bin/env python3
"""Tests for highlight bounds calculation.

This module tests the calc_highlight_bounds function used for
calculating padding around selected items in the file browser.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.highlights import calc_highlight_bounds


class TestCalcHighlightBounds:
    """Tests for calc_highlight_bounds function."""

    def test_room_for_both_paddings(self) -> None:
        """When plenty of room, returns (1, 1) padding."""
        assert calc_highlight_bounds(10, 15) == (1, 1)

    def test_room_for_left_padding_only(self) -> None:
        """When only 1 char available, left padding gets priority."""
        assert calc_highlight_bounds(10, 11) == (1, 0)

    def test_no_room_for_padding(self) -> None:
        """When content fills pane exactly, no padding."""
        assert calc_highlight_bounds(10, 10) == (0, 0)

    def test_content_exceeds_pane(self) -> None:
        """When content exceeds pane width, no padding."""
        assert calc_highlight_bounds(15, 10) == (0, 0)

    def test_zero_content_length(self) -> None:
        """Zero content length returns no padding."""
        assert calc_highlight_bounds(0, 10) == (0, 0)

    def test_zero_pane_width(self) -> None:
        """Zero pane width returns no padding."""
        assert calc_highlight_bounds(10, 0) == (0, 0)

    def test_negative_pane_width(self) -> None:
        """Negative pane width returns no padding."""
        assert calc_highlight_bounds(10, -5) == (0, 0)

    def test_negative_content_length(self) -> None:
        """Negative content length returns no padding."""
        assert calc_highlight_bounds(-5, 10) == (0, 0)

    def test_room_for_exactly_two_chars(self) -> None:
        """When exactly 2 chars available, both paddings get 1."""
        assert calc_highlight_bounds(8, 10) == (1, 1)
