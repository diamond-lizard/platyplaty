#!/usr/bin/env python3
"""Tests for navigation in empty and inaccessible directories.

This module tests:
- Navigation behavior (move_up, move_down, move_right, move_left) in empty directories
- Navigation behavior in directories that became inaccessible
- FileBrowser rendering of "inaccessible directory" message
"""

import sys
from pathlib import Path
from typing import Generator

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.nav_state import NavigationState
from platyplaty.ui.directory_types import DirectoryListing
from platyplaty.ui.file_browser_pane_render import render_pane_line

from helpers import make_inaccessible


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


class TestInaccessibleDirectoryRendering:
    """Tests for rendering of inaccessible directory message."""

    def test_renders_inaccessible_directory_message(self) -> None:
        """FileBrowser renders 'inaccessible directory' when permission_denied=True."""
        # Create a listing with permission_denied=True
        listing = DirectoryListing(
            entries=[],
            was_empty=False,
            had_filtered_entries=False,
            permission_denied=True,
        )
        
        # Render line 0 (the message line)
        result = render_pane_line(listing, y=0, width=30, is_left_pane=False)
        
        # Result is now list[Segment], check first segment text
        assert len(result) == 1, "should have one segment"
        segment_text = result[0].text
        assert "inaccessible directory" in segment_text, "should contain message"
        assert len(segment_text) == 30, "should be padded to width"
