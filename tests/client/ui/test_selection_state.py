#!/usr/bin/env python3
"""Tests for selection state tracking in the file browser.

This module tests:
- get_selected_name_for_directory() returns remembered name or None
- _calc_right_selection() returns remembered index or 0 if not found
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.nav_state import NavigationState
from platyplaty.ui.file_browser import FileBrowser
from platyplaty.ui.file_browser_refresh import _calc_right_selection
from platyplaty.ui.file_browser_types import RightPaneDirectory
from platyplaty.ui.directory import list_directory


class TestGetSelectedNameForDirectory:
    """Tests for get_selected_name_for_directory()."""

    def test_returns_none_if_never_visited(self, tmp_path: Path) -> None:
        """Directory never visited returns None."""
        parent = tmp_path / "parent"
        parent.mkdir()
        (parent / "alpha.milk").write_text("alpha")

        state = NavigationState(parent)

        # Query a directory we've never visited
        other_dir = tmp_path / "other"
        other_dir.mkdir()
        result = state.get_selected_name_for_directory(str(other_dir))

        assert result is None, "should return None for unvisited directory"

    def test_returns_remembered_name_after_visit(self, tmp_path: Path) -> None:
        """Directory visited returns remembered selection name."""
        parent = tmp_path / "parent"
        parent.mkdir()
        (parent / "alpha.milk").write_text("alpha")
        (parent / "beta.milk").write_text("beta")
        (parent / "gamma.milk").write_text("gamma")

        # Start in parent and select beta
        state = NavigationState(parent)
        state.move_down()  # alpha -> beta
        assert state.selected_name == "beta.milk"

        # Navigate away to save memory
        state.move_left()

        # Query the remembered selection
        result = state.get_selected_name_for_directory(str(parent))

        assert result == "beta.milk", "should return remembered name"

    def test_returns_none_for_current_dir_if_never_left(
        self, tmp_path: Path
    ) -> None:
        """Current directory returns None if we never navigated away."""
        parent = tmp_path / "parent"
        parent.mkdir()
        (parent / "alpha.milk").write_text("alpha")

        state = NavigationState(parent)

        # Query current directory without ever leaving
        result = state.get_selected_name_for_directory(str(parent))

        assert result is None, "memory only saved when navigating away"


class TestCalcRightSelection:
    """Tests for _calc_right_selection()."""

    def test_returns_zero_if_never_visited(self, tmp_path: Path) -> None:
        """Directory never visited returns index 0."""
        parent = tmp_path / "parent"
        parent.mkdir()
        (parent / "alpha.milk").write_text("alpha")
        subdir = parent / "subdir"
        subdir.mkdir()
        (subdir / "one.milk").write_text("one")
        (subdir / "two.milk").write_text("two")

        # Create FileBrowser starting in parent
        browser = FileBrowser({}, starting_dir=parent)

        # Select subdir
        browser.selected_index = 0  # subdir is first (dirs before files)
        browser._right_content = RightPaneDirectory(list_directory(subdir))

        # Never visited subdir, so remembered selection is None
        result = _calc_right_selection(browser, str(subdir))

        assert result == 0, "should return 0 for unvisited directory"

    def test_returns_remembered_index(self, tmp_path: Path) -> None:
        """Directory visited returns index of remembered selection."""
        parent = tmp_path / "parent"
        parent.mkdir()
        subdir = parent / "subdir"
        subdir.mkdir()
        (subdir / "alpha.milk").write_text("alpha")
        (subdir / "beta.milk").write_text("beta")
        (subdir / "gamma.milk").write_text("gamma")

        # Create FileBrowser and navigate into subdir
        browser = FileBrowser({}, starting_dir=parent)
        browser._nav_state.move_right()  # Enter subdir
        browser._nav_state.move_down()  # Select beta
        browser._nav_state.move_left()  # Back to parent, saves memory

        # Set up right pane to show subdir contents
        browser._right_content = RightPaneDirectory(list_directory(subdir))

        # Query should return index of "beta.milk" which is 1
        result = _calc_right_selection(browser, str(subdir))

        assert result == 1, "should return index of remembered name"

    def test_returns_zero_if_remembered_name_not_found(
        self, tmp_path: Path
    ) -> None:
        """Returns 0 if remembered name no longer exists in listing."""
        parent = tmp_path / "parent"
        parent.mkdir()
        subdir = parent / "subdir"
        subdir.mkdir()
        (subdir / "alpha.milk").write_text("alpha")
        (subdir / "beta.milk").write_text("beta")

        # Create FileBrowser and navigate into subdir
        browser = FileBrowser({}, starting_dir=parent)
        browser._nav_state.move_right()  # Enter subdir
        browser._nav_state.move_down()  # Select beta
        browser._nav_state.move_left()  # Back to parent, saves memory

        # Delete beta.milk
        (subdir / "beta.milk").unlink()

        # Set up right pane with updated listing (beta gone)
        browser._right_content = RightPaneDirectory(list_directory(subdir))

        # Query should return 0 since beta no longer exists
        result = _calc_right_selection(browser, str(subdir))

        assert result == 0, "should return 0 when remembered name not found"
