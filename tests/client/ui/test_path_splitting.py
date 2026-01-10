#!/usr/bin/env python3
"""Tests for path splitting into components.

This module tests TASK-0600: Path splitting into components.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.path_display import split_path_to_components
from platyplaty.ui.path_types import PathComponent, PathComponentType


class TestPathSplitting:
    """TASK-0600: Tests for path splitting into components."""

    def test_split_simple_path_returns_components(
        self, tmp_path: Path
    ) -> None:
        """Splitting a simple path returns correct components."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        components = split_path_to_components(subdir)
        assert len(components) > 0, "should have components"
        assert components[-1].name == "subdir", "last component is subdir"
        assert components[-1].is_selected is True, "last component is selected"

    def test_split_path_with_file_returns_file_component(
        self, tmp_path: Path
    ) -> None:
        """Splitting a path to a file marks file as final component."""
        test_file = tmp_path / "test.milk"
        test_file.write_text("content")
        components = split_path_to_components(test_file)
        assert components[-1].name == "test.milk"
        assert components[-1].component_type == PathComponentType.FILE

    def test_split_path_parent_components_are_directories(
        self, tmp_path: Path
    ) -> None:
        """All parent components should be directories."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        components = split_path_to_components(subdir)
        parent_types = [c.component_type for c in components[:-1]]
        allowed = {PathComponentType.DIRECTORY, PathComponentType.SYMLINK}
        assert all(t in allowed for t in parent_types), "parents must be dirs"

    def test_mark_selected_false_does_not_select_final(
        self, tmp_path: Path
    ) -> None:
        """REQ-0700: When mark_selected=False, final is not selected."""
        components = split_path_to_components(tmp_path, mark_selected=False)
        assert components[-1].is_selected is False
