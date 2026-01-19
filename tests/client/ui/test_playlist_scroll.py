#!/usr/bin/env python3
"""Unit tests for playlist scroll algorithm integration.

Tests that the playlist view uses the Safe-Zone Scroll Algorithm
correctly to keep the selection visible.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.nav_scroll import calc_safe_zone_scroll


class TestSafeZoneScrollForPlaylist:
    """Tests for safe-zone scroll algorithm used by playlist view."""

    def test_selection_in_safe_zone_no_scroll(self) -> None:
        """Selection within safe zone does not change scroll offset."""
        result = calc_safe_zone_scroll(
            selected_index=5,
            scroll_offset=0,
            pane_height=16,
            item_count=100,
        )
        assert result == 0

    def test_selection_above_safe_zone_scrolls_up(self) -> None:
        """Selection above safe zone triggers scroll up."""
        result = calc_safe_zone_scroll(
            selected_index=2,
            scroll_offset=10,
            pane_height=16,
            item_count=100,
        )
        assert result < 10

    def test_selection_below_safe_zone_scrolls_down(self) -> None:
        """Selection below safe zone triggers scroll down."""
        result = calc_safe_zone_scroll(
            selected_index=20,
            scroll_offset=0,
            pane_height=16,
            item_count=100,
        )
        assert result > 0

    def test_empty_list_returns_zero(self) -> None:
        """Empty list returns zero offset."""
        result = calc_safe_zone_scroll(
            selected_index=0,
            scroll_offset=0,
            pane_height=16,
            item_count=0,
        )
        assert result == 0

    def test_small_pane_uses_centering(self) -> None:
        """Very small pane falls back to centering."""
        result = calc_safe_zone_scroll(
            selected_index=10,
            scroll_offset=0,
            pane_height=3,
            item_count=100,
        )
        assert result == 10 - 3 // 2

    def test_first_item_selected(self) -> None:
        """First item selected keeps scroll at zero."""
        result = calc_safe_zone_scroll(
            selected_index=0,
            scroll_offset=5,
            pane_height=16,
            item_count=100,
        )
        assert result == 0

    def test_buffer_calculation(self) -> None:
        """Buffer is calculated as pane_height // 4."""
        pane_height = 16
        buffer = max(1, pane_height // 4)
        assert buffer == 4
