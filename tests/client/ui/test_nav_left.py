#!/usr/bin/env python3
"""Tests for left navigation (to parent directory) in the file browser.

This module tests:
- move_left() at filesystem root (no-op)
- move_left() sets selection to the directory we came from
- move_left() when parent is inaccessible
- move_left() updates current directory path to parent
- move_left() preserves logical path through symlinks
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.errors import InaccessibleDirectoryError
from platyplaty.ui.nav_state import NavigationState

from helpers import make_inaccessible, make_symlink_to_dir


class TestMoveLeft:
    """Tests for move_left() navigation."""

    def test_at_root_returns_false(self, tmp_path: Path) -> None:
        """TEST-0300: move_left() at filesystem root returns False."""
        # Navigate to root
        state = NavigationState(Path("/"))
        
        # Attempt to move left at root
        result = state.move_left()
        
        assert result is False, "should return False at root"
        assert state.current_dir == Path("/"), "should stay at root"

    def test_sets_selection_to_came_from_dir(self, temp_dir_tree: Path) -> None:
        """TEST-0400: move_left() sets selection to the directory we came from."""
        # Navigate into presets subdirectory
        presets = temp_dir_tree / "presets"
        state = NavigationState(presets)
        
        # Move left to parent
        result = state.move_left()
        
        assert result is True, "should return True on successful move"
        assert state.current_dir == temp_dir_tree, "should be in parent dir"
        assert state.selected_name == "presets", "should select the dir we came from"

    def test_inaccessible_parent_raises_error(self, temp_dir_tree: Path) -> None:
        """TEST-0500: move_left() when parent is inaccessible raises InaccessibleDirectoryError."""
        # Create nested structure: temp_dir_tree/parent/child
        parent = temp_dir_tree / "parent"
        parent.mkdir()
        child = parent / "child"
        child.mkdir()
        (child / "test.milk").write_text("test")
        
        # Start in child directory
        state = NavigationState(child)
        
        # Make parent inaccessible
        restore = make_inaccessible(parent)
        try:
            # Attempt to move left should raise error
            with pytest.raises(InaccessibleDirectoryError) as exc_info:
                state.move_left()
            assert str(parent) in str(exc_info.value), "error should contain path"
        finally:
            restore()

    def test_updates_current_dir_to_parent(self, temp_dir_tree: Path) -> None:
        """Move_left() updates current directory path to parent."""
        # Navigate into subdir subdirectory
        subdir = temp_dir_tree / "subdir"
        state = NavigationState(subdir)
        original_dir = state.current_dir
        
        # Move left to parent
        state.move_left()
        
        assert state.current_dir == temp_dir_tree, "current_dir should be parent"
        assert state.current_dir == original_dir.parent, "should equal original parent"

    def test_preserves_logical_path_through_symlink(self, temp_dir_tree: Path) -> None:
        """Move_left() preserves logical path when parent was reached through symlink."""
        # Create: temp_dir_tree/target/child and temp_dir_tree/link -> target
        target = temp_dir_tree / "target"
        target.mkdir()
        child = target / "child"
        child.mkdir()
        (child / "test.milk").write_text("test")
        
        link = temp_dir_tree / "link"
        make_symlink_to_dir(link, target)
        
        # Navigate through symlink: link/child
        logical_child = link / "child"
        state = NavigationState(logical_child)
        
        # Move left - should go to link, not target
        state.move_left()
        
        # Logical path should be through symlink
        assert state.current_dir == link, "should be at symlink, not resolved target"
        assert state.current_dir != target, "should not resolve to target"
