#!/usr/bin/env python3
"""Tests for startup and initialization behavior.

This module tests:
- FileBrowser initialization with inaccessible directories
- NavigationState initialization with valid directories
- Initial selection behavior
- Empty directory handling at startup
"""

import sys
from pathlib import Path
from typing import Generator

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.errors import InaccessibleDirectoryError
from platyplaty.ui.file_browser import FileBrowser
from platyplaty.ui.nav_state import NavigationState


class TestFileBrowserStartup:
    """Tests for FileBrowser initialization behavior."""

    def test_inaccessible_initial_directory_raises_error(
        self, tmp_path: Path, empty_dispatch_table: dict
    ) -> None:
        """TEST-0050: FileBrowser raises InaccessibleDirectoryError for inaccessible dir."""
        inaccessible = tmp_path / "noaccess"
        inaccessible.mkdir()
        inaccessible.chmod(0o000)
        try:
            with pytest.raises(InaccessibleDirectoryError) as exc_info:
                FileBrowser(empty_dispatch_table, starting_dir=inaccessible)
            assert str(inaccessible) in str(exc_info.value), "path should be in message"
        finally:
            inaccessible.chmod(0o755)


class TestNavigationStateStartup:
    """Tests for NavigationState initialization behavior."""

    def test_valid_directory_sets_correct_initial_state(
        self, temp_dir_tree: Path
    ) -> None:
        """NavigationState with valid directory sets current_dir correctly."""
        state = NavigationState(temp_dir_tree)
        assert state.current_dir == temp_dir_tree, "current_dir should match starting dir"
        assert state.scroll_offset == 0, "scroll_offset should start at 0"

    def test_initialization_selects_first_item(
        self, temp_dir_tree: Path
    ) -> None:
        """NavigationState selects first item when directory has contents."""
        state = NavigationState(temp_dir_tree)
        listing = state.get_listing()
        assert listing is not None, "listing should exist"
        assert len(listing.entries) > 0, "should have entries"
        # First item alphabetically should be selected
        first_name = listing.entries[0].name
        assert state.selected_name == first_name, "should select first item"

    def test_initialization_handles_empty_directory(
        self, tmp_path: Path
    ) -> None:
        """NavigationState handles empty directory correctly."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        state = NavigationState(empty_dir)
        assert state.current_dir == empty_dir, "current_dir should match"
        assert state.selected_name is None, "selected_name should be None for empty dir"
        listing = state.get_listing()
        assert listing is not None, "listing should exist"
        assert listing.was_empty is True, "was_empty should be True"
        assert len(listing.entries) == 0, "entries should be empty"
