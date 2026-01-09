#!/usr/bin/env python3
"""Tests for right navigation (into directories) in the file browser.

This module tests:
- move_right() on regular directory updates current path
- move_right() on inaccessible directory raises InaccessibleDirectoryError
- move_right() on broken symlink returns None (silent no-op)
- move_right() on symlink to inaccessible directory raises error
- move_right() on symlink to directory follows symlink
- Logical path is preserved when navigating through symlinks
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.errors import InaccessibleDirectoryError
from platyplaty.ui.nav_state import NavigationState

from helpers import make_broken_symlink, make_inaccessible, make_symlink_to_dir


class TestMoveRightDirectory:
    """Tests for move_right() navigation into directories."""


    def test_regular_dir_updates_path(self, temp_dir_tree: Path) -> None:
        """TEST-0600: move_right() on regular directory updates current path."""
        # Start in temp_dir_tree root
        state = NavigationState(temp_dir_tree)

        # Select and move into presets directory
        state.selected_name = "presets"
        result = state.move_right()

        assert result is None, "should return None for directory navigation"
        assert state.current_dir == temp_dir_tree / "presets", "should be in presets"

    def test_inaccessible_dir_raises_error(self, temp_dir_tree: Path) -> None:
        """TEST-0650: move_right() on inaccessible directory raises InaccessibleDirectoryError."""
        # Create an inaccessible subdirectory
        inaccessible = temp_dir_tree / "inaccessible"
        inaccessible.mkdir()
        (inaccessible / "test.milk").write_text("test")

        state = NavigationState(temp_dir_tree)
        state.selected_name = "inaccessible"

        # Make directory inaccessible
        restore = make_inaccessible(inaccessible)
        try:
            with pytest.raises(InaccessibleDirectoryError) as exc_info:
                state.move_right()
            assert str(inaccessible) in str(exc_info.value), "error should contain path"
        finally:
            restore()

    def test_broken_symlink_returns_none(self, temp_dir_tree: Path) -> None:
        """TEST-0700: move_right() on broken symlink returns None (silent no-op)."""
        # Create a broken symlink
        broken_link = temp_dir_tree / "broken.milk"
        make_broken_symlink(broken_link)

        state = NavigationState(temp_dir_tree)
        state.selected_name = "broken.milk"
        original_dir = state.current_dir

        result = state.move_right()

        assert result is None, "should return None for broken symlink"
        assert state.current_dir == original_dir, "should not navigate anywhere"

    def test_symlink_to_inaccessible_dir_raises_error(self, temp_dir_tree: Path) -> None:
        """TEST-0750: move_right() on symlink to inaccessible directory raises error."""
        # Create target directory and make it inaccessible
        target = temp_dir_tree / "target"
        target.mkdir()
        (target / "test.milk").write_text("test")

        # Create symlink to the target
        link = temp_dir_tree / "link_to_target"
        make_symlink_to_dir(link, target)

        state = NavigationState(temp_dir_tree)
        state.selected_name = "link_to_target"

        # Make target inaccessible
        restore = make_inaccessible(target)
        try:
            with pytest.raises(InaccessibleDirectoryError) as exc_info:
                state.move_right()
            assert "link_to_target" in str(exc_info.value) or str(target) in str(exc_info.value),                 "error should contain path"
        finally:
            restore()

    def test_symlink_to_dir_follows_and_updates_path(self, temp_dir_tree: Path) -> None:
        """Move_right() on symlink to directory follows symlink and updates logical path."""
        # Create target directory with content
        target = temp_dir_tree / "real_target"
        target.mkdir()
        (target / "inner.milk").write_text("inner content")

        # Create symlink to the target
        link = temp_dir_tree / "link_dir"
        make_symlink_to_dir(link, target)

        state = NavigationState(temp_dir_tree)
        state.selected_name = "link_dir"

        result = state.move_right()

        assert result is None, "should return None for directory navigation"
        # Logical path should be through symlink, not resolved target
        assert state.current_dir == temp_dir_tree / "link_dir", "should use symlink path"
        assert state.current_dir != target, "should not resolve to real target"

    def test_logical_path_preserved_through_symlinks(self, temp_dir_tree: Path) -> None:
        """TEST-1000: logical path is preserved when navigating through symlinks."""
        # Create nested structure: target/child
        target = temp_dir_tree / "target"
        target.mkdir()
        child = target / "child"
        child.mkdir()
        (child / "deep.milk").write_text("deep content")

        # Create symlink to target
        link = temp_dir_tree / "symlink"
        make_symlink_to_dir(link, target)

        # Navigate: start at root, go into symlink, then into child
        state = NavigationState(temp_dir_tree)
        state.selected_name = "symlink"
        state.move_right()

        # Now in symlink/, select child and navigate into it
        state.selected_name = "child"
        state.move_right()

        # Logical path should be through symlink, not resolved target
        expected = temp_dir_tree / "symlink" / "child"
        assert state.current_dir == expected, "should preserve logical path through symlink"
        assert "symlink" in str(state.current_dir), "path should contain symlink name"
        assert state.current_dir != target / "child", "should not resolve to target path"
