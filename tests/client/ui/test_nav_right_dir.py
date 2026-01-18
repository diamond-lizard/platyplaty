#!/usr/bin/env python3
"""Tests for right navigation into directories in the file browser.

This module tests:
- move_right() on regular directory updates current path
- move_right() on inaccessible directory raises InaccessibleDirectoryError
- move_right() on broken symlink returns None (silent no-op)
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.errors import InaccessibleDirectoryError
from platyplaty.ui.nav_state import NavigationState

from helpers import make_broken_symlink
from nav_right_helpers import temporarily_inaccessible


def test_regular_dir_updates_path(temp_dir_tree: Path) -> None:
    """TEST-0600: move_right() on regular directory updates current path."""
    state = NavigationState(temp_dir_tree)
    state.selected_name = "presets"
    result = state.move_right()

    assert result is None, "should return None for directory navigation"
    assert state.current_dir == temp_dir_tree / "presets", "should be in presets"


def test_inaccessible_dir_raises_error(temp_dir_tree: Path) -> None:
    """TEST-0650: move_right() on inaccessible directory raises error."""
    inaccessible = temp_dir_tree / "inaccessible"
    inaccessible.mkdir()
    (inaccessible / "test.milk").write_text("test")

    state = NavigationState(temp_dir_tree)
    state.selected_name = "inaccessible"

    with temporarily_inaccessible(inaccessible):
        with pytest.raises(InaccessibleDirectoryError) as exc_info:
            state.move_right()
        assert str(inaccessible) in str(exc_info.value), "error should contain path"


def test_broken_symlink_returns_none(temp_dir_tree: Path) -> None:
    """TEST-0700: move_right() on broken symlink returns None (silent no-op)."""
    broken_link = temp_dir_tree / "broken.milk"
    make_broken_symlink(broken_link)

    state = NavigationState(temp_dir_tree)
    state.selected_name = "broken.milk"
    original_dir = state.current_dir

    result = state.move_right()

    assert result is None, "should return None for broken symlink"
    assert state.current_dir == original_dir, "should not navigate anywhere"
