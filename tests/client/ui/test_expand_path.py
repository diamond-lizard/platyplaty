#!/usr/bin/env python3
"""Tests for expand_path function in command_parser module."""

import os
from pathlib import Path

from platyplaty.ui.command_parser import expand_path


class TestExpandPath:
    """Tests for expand_path function."""

    def test_absolute_path_unchanged(self) -> None:
        """Absolute paths are returned unchanged."""
        base = Path("/some/base")
        result = expand_path("/absolute/path/file.platy", base)
        assert result == Path("/absolute/path/file.platy")

    def test_relative_path_resolved(self) -> None:
        """Relative paths are resolved against base_dir."""
        base = Path("/some/base")
        result = expand_path("relative/file.platy", base)
        assert result == Path("/some/base/relative/file.platy")

    def test_tilde_expansion(self) -> None:
        """Tilde is expanded to home directory."""
        base = Path("/some/base")
        result = expand_path("~/file.platy", base)
        expected = Path.home() / "file.platy"
        assert result == expected

    def test_tilde_with_subdirectory(self) -> None:
        """Tilde with subdirectory is expanded."""
        base = Path("/some/base")
        result = expand_path("~/subdir/file.platy", base)
        expected = Path.home() / "subdir" / "file.platy"
        assert result == expected

    def test_env_var_expansion(self, monkeypatch) -> None:
        """Environment variables are expanded."""
        monkeypatch.setenv("TEST_DIR", "/test/directory")
        base = Path("/some/base")
        result = expand_path("$TEST_DIR/file.platy", base)
        assert result == Path("/test/directory/file.platy")

    def test_home_env_var(self, monkeypatch) -> None:
        """$HOME is expanded."""
        monkeypatch.setenv("HOME", "/home/testuser")
        base = Path("/some/base")
        result = expand_path("$HOME/file.platy", base)
        assert result == Path("/home/testuser/file.platy")

    def test_relative_dot_path(self) -> None:
        """Relative path with . is resolved."""
        base = Path("/some/base")
        result = expand_path("./file.platy", base)
        assert result == Path("/some/base/file.platy")

    def test_simple_filename(self) -> None:
        """Simple filename is resolved against base."""
        base = Path("/some/base")
        result = expand_path("file.platy", base)
        assert result == Path("/some/base/file.platy")
