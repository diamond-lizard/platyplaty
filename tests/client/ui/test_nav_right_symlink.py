#!/usr/bin/env python3
"""Tests for right navigation through symlinks in the file browser.

This module tests:
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

from helpers import make_symlink_to_dir
from nav_right_helpers import temporarily_inaccessible


def test_symlink_to_inaccessible_dir_raises_error(temp_dir_tree: Path) -> None:
    """TEST-0750: move_right() on symlink to inaccessible directory raises error."""
    target = temp_dir_tree / "target"
    target.mkdir()
    (target / "test.milk").write_text("test")

    link = temp_dir_tree / "link_to_target"
    make_symlink_to_dir(link, target)

    state = NavigationState(temp_dir_tree)
    state.selected_name = "link_to_target"

    with temporarily_inaccessible(target):
        with pytest.raises(InaccessibleDirectoryError) as exc_info:
            state.move_right()
        err_str = str(exc_info.value)
        assert "link_to_target" in err_str or str(target) in err_str


def test_symlink_to_dir_follows_and_updates_path(temp_dir_tree: Path) -> None:
    """move_right() on symlink to directory follows symlink and updates path."""
    target = temp_dir_tree / "real_target"
    target.mkdir()
    (target / "inner.milk").write_text("inner content")

    link = temp_dir_tree / "link_dir"
    make_symlink_to_dir(link, target)

    state = NavigationState(temp_dir_tree)
    state.selected_name = "link_dir"

    result = state.move_right()

    assert result is None, "should return None for directory navigation"
    assert state.current_dir == temp_dir_tree / "link_dir", "should use symlink path"
    assert state.current_dir != target, "should not resolve to real target"


def test_logical_path_preserved_through_symlinks(temp_dir_tree: Path) -> None:
    """TEST-1000: logical path is preserved when navigating through symlinks."""
    target = temp_dir_tree / "target"
    target.mkdir()
    child = target / "child"
    child.mkdir()
    (child / "deep.milk").write_text("deep content")

    link = temp_dir_tree / "symlink"
    make_symlink_to_dir(link, target)

    state = NavigationState(temp_dir_tree)
    state.selected_name = "symlink"
    state.move_right()

    state.selected_name = "child"
    state.move_right()

    expected = temp_dir_tree / "symlink" / "child"
    assert state.current_dir == expected, "should preserve logical path"
    assert "symlink" in str(state.current_dir), "path should contain symlink name"
    assert state.current_dir != target / "child", "should not resolve to target"
