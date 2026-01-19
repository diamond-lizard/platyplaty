#!/usr/bin/env python3
"""Tests for get_selected_name_for_directory() in NavigationState.

This module tests:
- get_selected_name_for_directory() returns remembered name or None
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.nav_state import NavigationState


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
