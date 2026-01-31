#!/usr/bin/env python3
"""Unit tests for cd navigation functions."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.commands.cd_navigate import is_same_directory


class TestIsSameDirectory:
    """Tests for is_same_directory function."""

    def test_identical_paths_return_true(self, tmp_path: Path) -> None:
        """Identical paths return True."""
        directory = tmp_path / "testdir"
        directory.mkdir()
        assert is_same_directory(directory, directory) is True

    def test_trailing_slash_vs_without_returns_true(self, tmp_path: Path) -> None:
        """Same path with trailing slash vs without returns True."""
        directory = tmp_path / "testdir"
        directory.mkdir()
        path_without = directory
        path_with = Path(str(directory) + "/")
        assert is_same_directory(path_without, path_with) is True

    def test_different_paths_return_false(self, tmp_path: Path) -> None:
        """Different paths return False."""
        dir1 = tmp_path / "dir1"
        dir2 = tmp_path / "dir2"
        dir1.mkdir()
        dir2.mkdir()
        assert is_same_directory(dir1, dir2) is False

    def test_symlink_and_target_return_false(self, tmp_path: Path) -> None:
        """Symlink and its target return False (different logical paths)."""
        target = tmp_path / "target"
        target.mkdir()
        link = tmp_path / "link"
        link.symlink_to(target)
        assert is_same_directory(link, target) is False

    def test_dotdot_normalization_returns_true(self, tmp_path: Path) -> None:
        """/foo/bar/.. and /foo return True (normpath resolves ..)."""
        parent = tmp_path / "foo"
        parent.mkdir()
        child = parent / "bar"
        child.mkdir()
        with_dotdot = child / ".."
        assert is_same_directory(with_dotdot, parent) is True

    def test_dot_normalization_returns_true(self, tmp_path: Path) -> None:
        """/foo/bar/. and /foo/bar return True (normpath removes .)."""
        directory = tmp_path / "foo" / "bar"
        directory.mkdir(parents=True)
        with_dot = directory / "."
        assert is_same_directory(with_dot, directory) is True

    def test_trailing_slash_normalized(self, tmp_path: Path) -> None:
        """/foo and /foo/ return True (trailing slash normalized)."""
        directory = tmp_path / "foo"
        directory.mkdir()
        without_slash = directory
        with_slash = Path(str(directory) + "/")
        assert is_same_directory(without_slash, with_slash) is True
