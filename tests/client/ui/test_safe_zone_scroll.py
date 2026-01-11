#!/usr/bin/env python3
"""Tests for the safe-zone scroll algorithm.

This module tests the calc_safe_zone_scroll function used for
calculating scroll offsets that keep the selection visible within
a comfortable viewing zone.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.nav_scroll import calc_safe_zone_scroll


class TestCalcSafeZoneScroll:
    """Tests for calc_safe_zone_scroll function."""

    def test_selection_within_safe_zone_no_change(self) -> None:
        """Selection in safe zone returns same scroll offset."""
        # 16-line pane, buffer=4, safe zone is rows 4-11
        # Selection at index 8 with scroll_offset=0 is within safe zone
        result = calc_safe_zone_scroll(8, 0, 16, 100)
        assert result == 0

    def test_selection_above_safe_zone(self) -> None:
        """Selection above safe zone scrolls up."""
        # Selection at index 2, scroll_offset=5, buffer=4
        # Selection is above safe zone (scroll+buffer=9)
        result = calc_safe_zone_scroll(2, 5, 16, 100)
        # Should scroll so selection is at buffer position
        assert result == 0

    def test_selection_below_safe_zone(self) -> None:
        """Selection below safe zone scrolls down."""
        # 16-line pane, buffer=4, scroll_offset=0
        # Safe zone bottom is scroll_offset + pane_height - buffer - 1 = 11
        # Selection at index 15 is below safe zone
        result = calc_safe_zone_scroll(15, 0, 16, 100)
        # Should adjust so selection is at bottom of safe zone
        assert result == 15 - 16 + 4 + 1  # index - pane_height + buffer + 1 = 4
        assert result == 4

    def test_small_pane_centering_fallback(self) -> None:
        """Very small pane falls back to centering."""
        # 4-line pane, buffer=1, 2*buffer >= pane_height triggers centering
        result = calc_safe_zone_scroll(10, 0, 4, 100)
        # Centered: index - pane_height // 2 = 10 - 2 = 8
        assert result == 8

    def test_boundary_no_negative_offset(self) -> None:
        """Scroll offset never goes negative."""
        result = calc_safe_zone_scroll(0, 0, 16, 100)
        assert result >= 0

    def test_boundary_no_empty_space_below(self) -> None:
        """Scroll offset respects max boundary (no empty space below)."""
        # 10 items, 16-line pane: max_offset = max(0, 10-16) = 0
        result = calc_safe_zone_scroll(5, 0, 16, 10)
        assert result == 0

    def test_boundary_large_list(self) -> None:
        """Scroll offset respects max boundary with large list."""
        # 100 items, 16-line pane: max_offset = 84
        # Selection at 95, should not scroll beyond 84
        result = calc_safe_zone_scroll(95, 80, 16, 100)
        assert result <= 84

    def test_zero_pane_height(self) -> None:
        """Zero pane height with centering fallback."""
        # This edge case: 2*buffer >= pane_height triggers centering
        result = calc_safe_zone_scroll(5, 0, 0, 100)
        # max_offset = max(0, 100-0) = 100, but offset is clamped
        assert result >= 0

    def test_single_item_list(self) -> None:
        """Single item list returns offset 0."""
        result = calc_safe_zone_scroll(0, 0, 16, 1)
        assert result == 0

    def test_selection_at_first_item(self) -> None:
        """Selection at first item returns offset 0."""
        result = calc_safe_zone_scroll(0, 5, 16, 100)
        assert result == 0

    def test_selection_at_last_item(self) -> None:
        """Selection at last item respects max boundary."""
        result = calc_safe_zone_scroll(99, 80, 16, 100)
        # max_offset = 84, should not exceed
        assert result <= 84
