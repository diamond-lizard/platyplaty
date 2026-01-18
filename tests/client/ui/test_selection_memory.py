#!/usr/bin/env python3
"""Tests for per-directory selection memory in the file browser."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.nav_state import NavigationState

from nav_memory_helpers import create_dir_with_milk_files


class TestSelectionMemory:
    """Tests for per-directory selection memory."""

    def test_selection_remembered_by_filename(self, tmp_path: Path) -> None:
        """TEST-1500: Selection is remembered by filename per directory path."""
        parent = tmp_path / "parent"
        create_dir_with_milk_files(parent, ["alpha", "beta", "gamma"])

        state = NavigationState(parent)
        assert state.selected_name == "alpha.milk", "initial selection"

        state.move_down()
        assert state.selected_name == "beta.milk", "should select beta"

        state.move_left()
        state.move_right()

        assert state.current_dir == parent, "should be in parent"
        assert state.selected_name == "beta.milk", "should remember selection"

    def test_remembered_filename_deleted_selects_topmost(
        self, tmp_path: Path
    ) -> None:
        """TEST-1500: When remembered filename no longer exists, topmost selected."""
        parent = tmp_path / "parent"
        create_dir_with_milk_files(parent, ["alpha", "beta", "gamma"])

        state = NavigationState(parent)
        state.move_down()
        assert state.selected_name == "beta.milk"

        state.move_left()
        (parent / "beta.milk").unlink()
        state.move_right()

        assert state.selected_name == "alpha.milk", "should select topmost"

    def test_first_visit_selects_topmost(self, tmp_path: Path) -> None:
        """First visit to directory selects topmost item."""
        test_dir = tmp_path / "test_dir"
        create_dir_with_milk_files(test_dir, ["alpha", "beta", "gamma"])

        state = NavigationState(test_dir)
        assert state.selected_name == "alpha.milk", "should select topmost"

    def test_navigating_away_and_back_restores_selection(
        self, tmp_path: Path
    ) -> None:
        """Navigating away and back restores remembered selection."""
        parent = tmp_path / "parent"
        create_dir_with_milk_files(parent, ["alpha", "beta", "gamma"])

        state = NavigationState(parent)
        state.move_down()
        state.move_down()
        assert state.selected_name == "gamma.milk"

        state.move_left()
        state.move_right()

        assert state.selected_name == "gamma.milk", "should restore selection"

    def test_selection_by_filename_not_index(self, tmp_path: Path) -> None:
        """Remembered selection is by filename, not by index."""
        parent = tmp_path / "parent"
        create_dir_with_milk_files(parent, ["alpha", "beta", "gamma"])

        state = NavigationState(parent)
        state.move_down()
        assert state.selected_name == "beta.milk"

        state.move_left()
        (parent / "aardvark.milk").write_text("aardvark")
        state.move_right()

        assert state.selected_name == "beta.milk", "should select by name"
