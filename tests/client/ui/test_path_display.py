#!/usr/bin/env python3
"""Tests for path display component model.

This module tests:
- Path splitting into components
- Symlink detection in path components
- Logical path preservation (not resolved target path)
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.path_display import (
    PathComponent,
    PathComponentType,
    split_path_to_components,
)


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
        for comp in components[:-1]:
            is_dir_or_sym = comp.component_type in (
                PathComponentType.DIRECTORY,
                PathComponentType.SYMLINK,
            )
            assert is_dir_or_sym, f"{comp.name} should be directory or symlink"

    def test_mark_selected_false_does_not_select_final(
        self, tmp_path: Path
    ) -> None:
        """REQ-0700: When mark_selected=False, final is not selected."""
        components = split_path_to_components(tmp_path, mark_selected=False)
        assert components[-1].is_selected is False


class TestSymlinkDetection:
    """TASK-0700: Tests for symlink detection in path components."""

    def test_symlink_in_path_detected_as_symlink(
        self, tmp_path: Path
    ) -> None:
        """Symlink components are detected with SYMLINK type."""
        target_dir = tmp_path / "target"
        target_dir.mkdir()
        link = tmp_path / "link"
        link.symlink_to(target_dir)
        components = split_path_to_components(link)
        assert components[-1].component_type == PathComponentType.SYMLINK

    def test_broken_symlink_detected_as_broken(
        self, tmp_path: Path
    ) -> None:
        """Broken symlinks are detected with BROKEN_SYMLINK type."""
        broken = tmp_path / "broken"
        broken.symlink_to(tmp_path / "nonexistent")
        components = split_path_to_components(broken)
        assert components[-1].component_type == PathComponentType.BROKEN_SYMLINK


class TestLogicalPath:
    """TASK-0800: Tests for logical path (not resolved target path)."""

    def test_symlink_path_uses_logical_not_resolved(
        self, tmp_path: Path
    ) -> None:
        """Path through symlink shows symlink name, not resolved target."""
        target_dir = tmp_path / "actual_target"
        target_dir.mkdir()
        link = tmp_path / "my_link"
        link.symlink_to(target_dir)
        nested_file = link / "file.milk"
        (target_dir / "file.milk").write_text("content")
        components = split_path_to_components(nested_file)
        names = [c.name for c in components]
        assert "my_link" in names, "symlink name should be in path"
        assert "actual_target" not in names, "resolved target should not be"
