#!/usr/bin/env python3
"""Tests for scroll adjustment behavior in the file browser."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.nav_state import NavigationState

from nav_memory_helpers import create_numbered_milk_files


class TestAdjustScroll:
    """Tests for adjust_scroll() visibility logic."""

    def test_adjust_scroll_below_visible(self, tmp_path: Path) -> None:
        """Adjust_scroll() keeps selection visible when below visible area."""
        test_dir = tmp_path / "test_dir"
        create_numbered_milk_files(test_dir, 20)

        state = NavigationState(test_dir)
        state.scroll_offset = 0

        for _ in range(15):
            state.move_down()
        assert state.selected_name == "file_15.milk"

        state.adjust_scroll(pane_height=10)
        assert state.scroll_offset >= 6, "scroll should move to show selection"
        assert state.scroll_offset <= 15, "selection should be visible"

    def test_adjust_scroll_above_visible(self, tmp_path: Path) -> None:
        """Adjust_scroll() keeps selection visible when above visible area."""
        test_dir = tmp_path / "test_dir"
        create_numbered_milk_files(test_dir, 20)

        state = NavigationState(test_dir)
        for _ in range(15):
            state.move_down()
        state.scroll_offset = 10

        for _ in range(10):
            state.move_up()
        assert state.selected_name == "file_05.milk"

        state.adjust_scroll(pane_height=10)
        assert state.scroll_offset <= 5, "scroll should move to show selection"

    def test_adjust_scroll_no_op_when_visible(self, tmp_path: Path) -> None:
        """Adjust_scroll() is no-op when selection already visible."""
        test_dir = tmp_path / "test_dir"
        create_numbered_milk_files(test_dir, 20)

        state = NavigationState(test_dir)
        for _ in range(5):
            state.move_down()
        state.scroll_offset = 0
        assert state.selected_name == "file_05.milk"

        state.adjust_scroll(pane_height=10)
        assert state.scroll_offset == 0, "scroll should not change"

    def test_scroll_offset_clamps_at_zero(self, tmp_path: Path) -> None:
        """Scroll_offset clamps at 0 (no empty lines above first item)."""
        test_dir = tmp_path / "test_dir"
        create_numbered_milk_files(test_dir, 10)

        state = NavigationState(test_dir)
        state.selected_name = "file_00.milk"
        state.scroll_offset = -5

        state.adjust_scroll(pane_height=5)
        assert state.scroll_offset >= 0, "scroll_offset should not be negative"
