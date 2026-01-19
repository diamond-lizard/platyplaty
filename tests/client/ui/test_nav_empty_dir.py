#!/usr/bin/env python3
"""Tests for navigation in empty directories.

This module tests navigation behavior (move_up, move_down, move_right,
move_left) in empty directories.
"""

import sys
from pathlib import Path
from typing import Generator

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.nav_state import NavigationState


class TestEmptyDirectory:
    """Tests for navigation in empty directories."""

    @pytest.fixture
    def empty_dir_state(self, tmp_path: Path) -> Generator[NavigationState, None, None]:
        """Create a NavigationState for an empty directory.

        Args:
            tmp_path: Pytest's tmp_path fixture.

        Yields:
            NavigationState initialized to an empty directory.
        """
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        state = NavigationState(empty_dir)
        yield state

    def test_move_up_is_no_op(self, empty_dir_state: NavigationState) -> None:
        """Move_up() in empty directory is no-op."""
        result = empty_dir_state.move_up()
        assert result is False, "should return False in empty directory"
        assert empty_dir_state.selected_name is None, "selection should remain None"

    def test_move_down_is_no_op(self, empty_dir_state: NavigationState) -> None:
        """Move_down() in empty directory is no-op."""
        result = empty_dir_state.move_down()
        assert result is False, "should return False in empty directory"
        assert empty_dir_state.selected_name is None, "selection should remain None"

    def test_move_right_is_no_op(self, empty_dir_state: NavigationState) -> None:
        """Move_right() in empty directory is no-op."""
        result = empty_dir_state.move_right()
        assert result is None, "should return None in empty directory"
        assert empty_dir_state.selected_name is None, "selection should remain None"

    def test_move_left_still_navigates(self, empty_dir_state: NavigationState) -> None:
        """Move_left() in empty directory still navigates to parent."""
        original_dir = empty_dir_state.current_dir
        parent_dir = original_dir.parent

        result = empty_dir_state.move_left()

        assert result is True, "should return True for successful navigation"
        assert empty_dir_state.current_dir == parent_dir, "should navigate to parent"
        assert empty_dir_state.selected_name == original_dir.name, "should select the dir we came from"
