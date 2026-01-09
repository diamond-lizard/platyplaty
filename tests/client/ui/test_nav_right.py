#!/usr/bin/env python3
"""Tests for right navigation (into directories and files) in the file browser.

This module tests:
- move_right() on regular directory updates current path
- move_right() on inaccessible directory raises InaccessibleDirectoryError
- move_right() on broken symlink returns None (silent no-op)
- move_right() on symlink to inaccessible directory raises error
- move_right() on symlink to directory follows symlink
- Logical path is preserved when navigating through symlinks
- move_right() on regular file returns path for editor
- move_right() on symlink to file returns symlink path for editor
- refresh_after_editor() keeps selection when file exists
- refresh_after_editor() moves selection when file deleted
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.errors import InaccessibleDirectoryError
from platyplaty.ui.nav_state import NavigationState

from helpers import make_broken_symlink, make_inaccessible, make_symlink_to_dir, make_symlink_to_file


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


class TestMoveRightFile:
    """Tests for move_right() navigation on files."""

    def test_regular_file_returns_path(self, temp_dir_tree: Path) -> None:
        """move_right() on regular file returns path for editor."""
        state = NavigationState(temp_dir_tree)
        # Select alpha.milk (a regular file)
        state.selected_name = "alpha.milk"
        
        result = state.move_right()
        
        expected = str(temp_dir_tree / "alpha.milk")
        assert result == expected, "should return logical path to file"

    def test_symlink_to_file_returns_symlink_path(self, temp_dir_tree: Path) -> None:
        """move_right() on symlink to file returns symlink path, not resolved target."""
        # Create target file and symlink to it
        target = temp_dir_tree / "target.milk"
        target.write_text("target content")
        link = temp_dir_tree / "link.milk"
        make_symlink_to_file(link, target)
        
        state = NavigationState(temp_dir_tree)
        state.selected_name = "link.milk"
        
        result = state.move_right()
        
        expected = str(temp_dir_tree / "link.milk")
        assert result == expected, "should return symlink path, not resolved target"
        assert result != str(target), "should not return resolved target path"

    def test_refresh_after_editor_keeps_selection_when_file_exists(
        self, temp_dir_tree: Path
    ) -> None:
        """refresh_after_editor() keeps selection on same filename when file exists."""
        state = NavigationState(temp_dir_tree)
        state.selected_name = "beta.milk"
        
        # Simulate editor return - file still exists
        state.refresh_after_editor()
        
        assert state.selected_name == "beta.milk", "selection should stay on same file"

    def test_refresh_after_editor_moves_to_next_when_file_deleted(
        self, temp_dir_tree: Path
    ) -> None:
        """TEST-1600: refresh_after_editor() moves selection to item below when file deleted."""
        state = NavigationState(temp_dir_tree)
        # Select beta.milk (middle of list: alpha, beta, gamma, presets, subdir)
        state.selected_name = "beta.milk"
        
        # Delete the file (simulating external deletion while in editor)
        (temp_dir_tree / "beta.milk").unlink()
        
        state.refresh_after_editor()
        
        # Should move to item that was at beta's index (gamma.milk)
        assert state.selected_name == "gamma.milk", \
            "selection should move to item at previous index"

    def test_refresh_after_editor_moves_to_last_when_bottom_deleted(
        self, temp_dir_tree: Path
    ) -> None:
        """refresh_after_editor() moves to new last item when bottom item deleted."""
        # Create a directory with only a few items for easier testing
        test_dir = temp_dir_tree / "test_subdir"
        test_dir.mkdir()
        (test_dir / "first.milk").write_text("first")
        (test_dir / "second.milk").write_text("second")
        (test_dir / "third.milk").write_text("third")
        
        state = NavigationState(test_dir)
        # Select last item (third.milk - sorted alphabetically)
        state.selected_name = "third.milk"
        
        # Delete the last file
        (test_dir / "third.milk").unlink()
        
        state.refresh_after_editor()
        
        # Should move to new last item (second.milk)
        assert state.selected_name == "second.milk", \
            "selection should move to new last item"
