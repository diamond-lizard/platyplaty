#!/usr/bin/env python3
"""Tests for right navigation on files in the file browser.

This module tests:
- move_right() on regular file returns path for editor
- move_right() on symlink to file returns symlink path for editor
- refresh_after_editor() keeps selection when file exists
- refresh_after_editor() moves selection when file deleted
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.nav_state import NavigationState

from helpers import make_symlink_to_file


def test_regular_file_returns_path(temp_dir_tree: Path) -> None:
    """move_right() on regular file returns path for editor."""
    state = NavigationState(temp_dir_tree)
    state.selected_name = "alpha.milk"

    result = state.move_right()

    expected = str(temp_dir_tree / "alpha.milk")
    assert result == expected, "should return logical path to file"


def test_symlink_to_file_returns_symlink_path(temp_dir_tree: Path) -> None:
    """move_right() on symlink to file returns symlink path, not resolved target."""
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
    temp_dir_tree: Path
) -> None:
    """refresh_after_editor() keeps selection on same filename when file exists."""
    state = NavigationState(temp_dir_tree)
    state.selected_name = "beta.milk"

    state.refresh_after_editor()

    assert state.selected_name == "beta.milk", "selection should stay on same file"


def test_refresh_after_editor_moves_to_next_when_file_deleted(
    temp_dir_tree: Path
) -> None:
    """TEST-1600: refresh_after_editor() moves selection when file deleted."""
    state = NavigationState(temp_dir_tree)
    state.selected_name = "beta.milk"

    (temp_dir_tree / "beta.milk").unlink()

    state.refresh_after_editor()

    assert state.selected_name == "gamma.milk", "should move to item at previous index"


def test_refresh_after_editor_moves_to_last_when_bottom_deleted(
    temp_dir_tree: Path
) -> None:
    """refresh_after_editor() moves to new last item when bottom item deleted."""
    test_dir = temp_dir_tree / "test_subdir"
    test_dir.mkdir()
    (test_dir / "first.milk").write_text("first")
    (test_dir / "second.milk").write_text("second")
    (test_dir / "third.milk").write_text("third")

    state = NavigationState(test_dir)
    state.selected_name = "third.milk"

    (test_dir / "third.milk").unlink()

    state.refresh_after_editor()

    assert state.selected_name == "second.milk", "should move to new last item"
