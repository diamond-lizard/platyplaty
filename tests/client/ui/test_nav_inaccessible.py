#!/usr/bin/env python3
"""Tests for navigation in directories that became inaccessible.

This module tests navigation behavior (move_up, move_down, move_right,
move_left) in directories where the user has lost read permission.
"""

import sys
from pathlib import Path
from typing import Generator

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.nav_state import NavigationState

from helpers import make_inaccessible


class TestInaccessibleDirectory:
    """Tests for navigation in directories that became inaccessible.

    The fixture initializes NavigationState with an accessible directory,
    then makes it inaccessible and calls refresh_after_editor() to detect
    the permission change.
    """

    @pytest.fixture
    def inaccessible_state(
        self, tmp_path: Path
    ) -> Generator[tuple[NavigationState, Path], None, None]:
        """Create a NavigationState for a directory that became inaccessible.

        Creates a directory with a .milk file, initializes NavigationState,
        then makes the directory inaccessible and refreshes state.

        Yields:
            Tuple of (NavigationState, parent_path) for assertions.
        """
        # Create directory with content
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        (test_dir / "test.milk").write_text("test content")

        # Initialize state while directory is accessible
        state = NavigationState(test_dir)

        # Make directory inaccessible
        restore = make_inaccessible(test_dir)
        try:
            # Refresh to detect permission change
            state.refresh_after_editor()
            yield state, tmp_path
        finally:
            restore()

    def test_move_up_is_no_op(
        self, inaccessible_state: tuple[NavigationState, Path]
    ) -> None:
        """Move_up() in inaccessible directory is no-op."""
        state, _ = inaccessible_state
        result = state.move_up()
        assert result is False, "should return False in inaccessible directory"

    def test_move_down_is_no_op(
        self, inaccessible_state: tuple[NavigationState, Path]
    ) -> None:
        """Move_down() in inaccessible directory is no-op."""
        state, _ = inaccessible_state
        result = state.move_down()
        assert result is False, "should return False in inaccessible directory"

    def test_move_right_is_no_op(
        self, inaccessible_state: tuple[NavigationState, Path]
    ) -> None:
        """Move_right() in inaccessible directory is no-op."""
        state, _ = inaccessible_state
        result = state.move_right()
        assert result is None, "should return None in inaccessible directory"

    def test_move_left_still_navigates(
        self, inaccessible_state: tuple[NavigationState, Path]
    ) -> None:
        """Move_left() in inaccessible directory still navigates to parent."""
        state, parent_path = inaccessible_state
        original_dir = state.current_dir

        result = state.move_left()

        assert result is True, "should return True for successful navigation"
        assert state.current_dir == parent_path, "should navigate to parent"
        assert state.selected_name == original_dir.name, "should select the dir we came from"
