#!/usr/bin/env python3
"""Tests for symlink detection and logical path handling.

This module tests:
- TASK-0700: Symlink detection in path components
- TASK-0800: Logical path preservation (not resolved target path)
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.path_display import split_path_to_components
from platyplaty.ui.path_types import PathComponent, PathComponentType


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
