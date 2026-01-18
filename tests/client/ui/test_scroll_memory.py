#!/usr/bin/env python3
"""Tests for per-directory scroll position memory in the file browser."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.nav_state import NavigationState

from nav_memory_helpers import create_numbered_milk_files


class TestScrollMemory:
    """Tests for per-directory scroll position memory."""

    def test_scroll_position_stored_per_directory(self, tmp_path: Path) -> None:
        """TEST-1100: Scroll position is stored in per-directory memory."""
        parent = tmp_path / "parent"
        create_numbered_milk_files(parent, 20)

        state = NavigationState(parent)
        state.scroll_offset = 5

        for _ in range(8):
            state.move_down()

        state.move_left()
        assert state.scroll_offset == 0, "scroll resets in new dir"

        state.move_right()
        assert state.scroll_offset == 5, "should remember scroll position"

    def test_left_pane_inherits_scroll_from_middle(
        self, tmp_path: Path
    ) -> None:
        """TEST-1100: Left pane inherits scroll from middle when navigating right."""
        parent = tmp_path / "parent"
        parent.mkdir()
        subdir = parent / "subdir"
        subdir.mkdir()
        (subdir / "test.milk").write_text("test")

        create_numbered_milk_files(parent, 20)

        state = NavigationState(parent)
        state.scroll_offset = 7
        state.selected_name = "subdir"
        state.move_right()

        parent_scroll = state.get_parent_scroll_offset()
        assert parent_scroll == 7, "left pane should inherit scroll"
