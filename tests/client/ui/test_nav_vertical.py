#!/usr/bin/env python3
"""Tests for up/down navigation in the file browser.

This module tests:
- move_up() boundary behavior (clamping at index 0)
- move_down() boundary behavior (clamping at max index)
- Selection changes when moving within a list
- No-op behavior at boundaries
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.nav_state import NavigationState


class TestMoveUp:
    """Tests for move_up() navigation."""

    def test_clamps_at_index_zero(self, nav_state: NavigationState) -> None:
        """TEST-0100: move_up() clamps at index 0 (does not go negative)."""
        # Start at first item
        listing = nav_state.get_listing()
        assert listing is not None, "listing should exist"
        first_name = listing.entries[0].name
        nav_state.selected_name = first_name
        
        # Attempt to move up past the beginning
        for _ in range(5):
            nav_state.move_up()
        
        # Selection should stay at first item
        assert nav_state.selected_name == first_name, "should stay at first item"

    def test_from_middle_decrements_selection(self, nav_state: NavigationState) -> None:
        """Move up from middle of list decrements selection index."""
        listing = nav_state.get_listing()
        assert listing is not None, "listing should exist"
        assert len(listing.entries) >= 3, "need at least 3 entries"
        
        # Move to second item
        second_name = listing.entries[1].name
        first_name = listing.entries[0].name
        nav_state.selected_name = second_name
        
        # Move up should go to first item
        result = nav_state.move_up()
        assert result is True, "should return True on successful move"
        assert nav_state.selected_name == first_name, "should select first item"

    def test_at_top_returns_false(self, nav_state: NavigationState) -> None:
        """Move_up() at index 0 is silent no-op (returns False, stays at 0)."""
        listing = nav_state.get_listing()
        assert listing is not None, "listing should exist"
        first_name = listing.entries[0].name
        nav_state.selected_name = first_name
        
        # Move up at first item should return False
        result = nav_state.move_up()
        assert result is False, "should return False at top"
        assert nav_state.selected_name == first_name, "should stay at first item"


class TestMoveDown:
    """Tests for move_down() navigation."""

    def test_clamps_at_max_index(self, nav_state: NavigationState) -> None:
        """TEST-0200: move_down() clamps at max index (does not exceed list length)."""
        listing = nav_state.get_listing()
        assert listing is not None, "listing should exist"
        assert len(listing.entries) > 0, "should have entries"
        
        # Move to last item
        last_name = listing.entries[-1].name
        nav_state.selected_name = last_name
        
        # Attempt to move down past the end
        for _ in range(5):
            nav_state.move_down()
        
        # Selection should stay at last item
        assert nav_state.selected_name == last_name, "should stay at last item"

    def test_from_middle_increments_selection(self, nav_state: NavigationState) -> None:
        """Move down from middle of list increments selection index."""
        listing = nav_state.get_listing()
        assert listing is not None, "listing should exist"
        assert len(listing.entries) >= 3, "need at least 3 entries"
        
        # Start at first item
        first_name = listing.entries[0].name
        second_name = listing.entries[1].name
        nav_state.selected_name = first_name
        
        # Move down should go to second item
        result = nav_state.move_down()
        assert result is True, "should return True on successful move"
        assert nav_state.selected_name == second_name, "should select second item"

    def test_at_bottom_returns_false(self, nav_state: NavigationState) -> None:
        """Move_down() at last index is silent no-op (returns False, stays at max)."""
        listing = nav_state.get_listing()
        assert listing is not None, "listing should exist"
        last_name = listing.entries[-1].name
        nav_state.selected_name = last_name
        
        # Move down at last item should return False
        result = nav_state.move_down()
        assert result is False, "should return False at bottom"
        assert nav_state.selected_name == last_name, "should stay at last item"
