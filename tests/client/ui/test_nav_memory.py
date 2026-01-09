#!/usr/bin/env python3
"""Tests for selection and scroll memory in the file browser.

This module tests:
- Per-directory selection memory by filename
- Per-directory scroll position memory
- First visit behavior (topmost item selected)
- Scroll adjustment to keep selection visible
"""

import sys
from pathlib import Path
from typing import Generator

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.nav_state import NavigationState


class TestSelectionMemory:
    """Tests for per-directory selection memory."""

    def test_selection_remembered_by_filename(self, tmp_path: Path) -> None:
        """TEST-1500: Selection is remembered by filename per directory path."""
        # Create structure: tmp_path contains "parent" dir with files
        parent = tmp_path / "parent"
        parent.mkdir()
        (parent / "alpha.milk").write_text("alpha")
        (parent / "beta.milk").write_text("beta")
        (parent / "gamma.milk").write_text("gamma")

        # Initialize state in parent, starting at first item (alpha)
        state = NavigationState(parent)
        assert state.selected_name == "alpha.milk", "initial selection"

        # Move down to select "beta.milk"
        state.move_down()
        assert state.selected_name == "beta.milk", "should select beta"

        # Navigate to parent of parent (move_left saves memory for parent)
        state.move_left()
        assert state.current_dir == tmp_path, "should be in tmp_path"
        assert state.selected_name == "parent", "should select parent dir"

        # Navigate back into parent (move_right restores memory)
        state.move_right()

        # Selection should be restored to "beta.milk"
        assert state.current_dir == parent, "should be in parent"
        assert state.selected_name == "beta.milk", "should remember selection"

    def test_remembered_filename_deleted_selects_topmost(self, tmp_path: Path) -> None:
        """TEST-1500: When remembered filename no longer exists, topmost item is selected."""
        # Create parent with files
        parent = tmp_path / "parent"
        parent.mkdir()
        alpha_file = parent / "alpha.milk"
        alpha_file.write_text("alpha")
        (parent / "beta.milk").write_text("beta")
        (parent / "gamma.milk").write_text("gamma")

        # Initialize state, move to beta
        state = NavigationState(parent)
        state.move_down()
        assert state.selected_name == "beta.milk", "should select beta"

        # Navigate away (saves memory with beta selected)
        state.move_left()

        # Delete beta.milk while we're away
        (parent / "beta.milk").unlink()

        # Navigate back
        state.move_right()

        # Since beta.milk no longer exists, topmost item should be selected
        assert state.current_dir == parent, "should be in parent"
        assert state.selected_name == "alpha.milk", "should select topmost item"

    def test_first_visit_selects_topmost(self, tmp_path: Path) -> None:
        """First visit to directory selects topmost item."""
        # Create directory with files
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        (test_dir / "alpha.milk").write_text("alpha")
        (test_dir / "beta.milk").write_text("beta")
        (test_dir / "gamma.milk").write_text("gamma")

        # Initialize state - first visit
        state = NavigationState(test_dir)

        # Topmost item should be selected
        assert state.selected_name == "alpha.milk", "should select topmost item"

    def test_navigating_away_and_back_restores_selection(self, tmp_path: Path) -> None:
        """Navigating away and back restores remembered selection."""
        # Create directory with files
        parent = tmp_path / "parent"
        parent.mkdir()
        (parent / "alpha.milk").write_text("alpha")
        (parent / "beta.milk").write_text("beta")
        (parent / "gamma.milk").write_text("gamma")

        # Initialize state in parent
        state = NavigationState(parent)

        # Move to gamma.milk
        state.move_down()  # alpha -> beta
        state.move_down()  # beta -> gamma
        assert state.selected_name == "gamma.milk", "should select gamma"

        # Navigate to parent's parent (saves memory)
        state.move_left()
        assert state.current_dir == tmp_path, "should be in tmp_path"

        # Navigate back into parent
        state.move_right()

        # Selection should be restored to gamma.milk
        assert state.current_dir == parent, "should be in parent"
        assert state.selected_name == "gamma.milk", "should restore selection"

    def test_selection_by_filename_not_index(self, tmp_path: Path) -> None:
        """Remembered selection is by filename, not by index."""
        # Create directory with files
        parent = tmp_path / "parent"
        parent.mkdir()
        (parent / "alpha.milk").write_text("alpha")
        (parent / "beta.milk").write_text("beta")
        (parent / "gamma.milk").write_text("gamma")

        # Initialize state, select beta (index 1)
        state = NavigationState(parent)
        state.move_down()  # alpha -> beta
        assert state.selected_name == "beta.milk", "should select beta"

        # Navigate away
        state.move_left()

        # Add a new file that would sort before beta
        (parent / "aardvark.milk").write_text("aardvark")

        # Navigate back
        state.move_right()

        # Selection should still be beta.milk (by name), not index 1
        assert state.selected_name == "beta.milk", "should select by name not index"


class TestScrollMemory:
    """Tests for per-directory scroll position memory."""

    def test_scroll_position_stored_per_directory(self, tmp_path: Path) -> None:
        """TEST-1100: Scroll position is stored in per-directory memory."""
        # Create directory with many files to enable scrolling
        parent = tmp_path / "parent"
        parent.mkdir()
        for i in range(20):
            name = f"file_{i:02d}.milk"
            (parent / name).write_text(f"content {i}")

        # Initialize state
        state = NavigationState(parent)

        # Simulate scrolling by setting scroll_offset
        state.scroll_offset = 5

        # Move down a few times to change selection
        for _ in range(8):
            state.move_down()

        # Navigate away (saves memory with scroll_offset)
        state.move_left()
        assert state.scroll_offset == 0, "scroll resets in new dir"

        # Navigate back
        state.move_right()

        # Scroll offset should be restored
        assert state.scroll_offset == 5, "should remember scroll position"

    def test_left_pane_inherits_scroll_from_middle(self, tmp_path: Path) -> None:
        """TEST-1100: Left pane inherits scroll position from middle pane when navigating right."""
        # Create parent with subdir
        parent = tmp_path / "parent"
        parent.mkdir()
        subdir = parent / "subdir"
        subdir.mkdir()
        (subdir / "test.milk").write_text("test")

        # Create many files in parent to enable scrolling
        for i in range(20):
            name = f"file_{i:02d}.milk"
            (parent / name).write_text(f"content {i}")

        # Initialize state in parent
        state = NavigationState(parent)

        # Set a scroll offset
        state.scroll_offset = 7

        # Navigate into subdir - this saves parent's scroll offset
        state.selected_name = "subdir"
        state.move_right()

        # The left pane (parent) should have the scroll offset we set
        parent_scroll = state.get_parent_scroll_offset()
        assert parent_scroll == 7, "left pane should inherit scroll from middle"

    def test_adjust_scroll_below_visible(self, tmp_path: Path) -> None:
        """Adjust_scroll() keeps selection visible when selection moves below visible area."""
        # Create directory with many files
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        for i in range(20):
            name = f"file_{i:02d}.milk"
            (test_dir / name).write_text(f"content {i}")

        # Initialize state
        state = NavigationState(test_dir)
        state.scroll_offset = 0

        # Move selection to item 15 (beyond visible area with pane_height=10)
        for _ in range(15):
            state.move_down()
        assert state.selected_name == "file_15.milk", "should select file_15"

        # Adjust scroll with pane height of 10
        state.adjust_scroll(pane_height=10)

        # Scroll should have moved to keep selection visible
        # Selection at index 15 with pane height 10 means scroll should be at least 6
        assert state.scroll_offset >= 6, "scroll should move to show selection"
        assert state.scroll_offset <= 15, "selection should be visible"

    def test_adjust_scroll_above_visible(self, tmp_path: Path) -> None:
        """Adjust_scroll() keeps selection visible when selection moves above visible area."""
        # Create directory with many files
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        for i in range(20):
            name = f"file_{i:02d}.milk"
            (test_dir / name).write_text(f"content {i}")

        # Initialize state
        state = NavigationState(test_dir)

        # Move down to item 15, then set scroll to show items 10-19
        for _ in range(15):
            state.move_down()
        state.scroll_offset = 10

        # Now move selection up to item 5 (above visible area)
        for _ in range(10):
            state.move_up()
        assert state.selected_name == "file_05.milk", "should select file_05"

        # Adjust scroll with pane height of 10
        state.adjust_scroll(pane_height=10)

        # Scroll should have moved to show selection (item 5)
        assert state.scroll_offset <= 5, "scroll should move to show selection"

    def test_adjust_scroll_no_op_when_visible(self, tmp_path: Path) -> None:
        """Adjust_scroll() is no-op when selection already visible."""
        # Create directory with many files
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        for i in range(20):
            name = f"file_{i:02d}.milk"
            (test_dir / name).write_text(f"content {i}")

        # Initialize state
        state = NavigationState(test_dir)

        # Move to item 5 and set scroll to show items 0-9
        for _ in range(5):
            state.move_down()
        state.scroll_offset = 0
        assert state.selected_name == "file_05.milk", "should select file_05"

        # Adjust scroll with pane height of 10 - selection at 5 is visible
        state.adjust_scroll(pane_height=10)

        # Scroll should remain at 0 (no change needed)
        assert state.scroll_offset == 0, "scroll should not change"

    def test_scroll_offset_clamps_at_zero(self, tmp_path: Path) -> None:
        """Scroll_offset clamps at 0 (no empty lines above first item)."""
        # Create directory with files
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        for i in range(10):
            name = f"file_{i:02d}.milk"
            (test_dir / name).write_text(f"content {i}")

        # Initialize state
        state = NavigationState(test_dir)

        # Set selection to first item
        state.selected_name = "file_00.milk"

        # Try to set a negative scroll offset manually
        state.scroll_offset = -5

        # Adjust scroll should clamp to 0
        state.adjust_scroll(pane_height=5)

        # Scroll offset should be clamped to 0
        assert state.scroll_offset >= 0, "scroll_offset should not be negative"
