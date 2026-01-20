#!/usr/bin/env python3
"""Unit tests for :load command error handling."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.commands.load_helpers import (
    expand_command_path,
    validate_playlist_path,
)


class TestValidatePlaylistPath:
    """Tests for validate_playlist_path function."""

    def test_file_not_found_returns_error(self, tmp_path: Path) -> None:
        """validate_playlist_path returns error for non-existent file."""
        nonexistent = tmp_path / "does_not_exist.platy"
        error = validate_playlist_path(nonexistent)
        assert error is not None
        assert "file not found" in error
        assert str(nonexistent) in error

    def test_directory_returns_error(self, tmp_path: Path) -> None:
        """validate_playlist_path returns error for directory."""
        error = validate_playlist_path(tmp_path)
        assert error is not None
        assert "not a file" in error

    def test_valid_file_returns_none(self, tmp_path: Path) -> None:
        """validate_playlist_path returns None for valid file."""
        valid_file = tmp_path / "test.platy"
        valid_file.write_text("/test.milk\n")
        error = validate_playlist_path(valid_file)
        assert error is None


class TestExpandCommandPath:
    """Tests for expand_command_path function."""

    def test_absolute_path_unchanged(self, tmp_path: Path) -> None:
        """Absolute paths are returned unchanged."""
        result = expand_command_path("/abs/path.platy", tmp_path)
        assert result == Path("/abs/path.platy")

    def test_relative_path_resolved(self, tmp_path: Path) -> None:
        """Relative paths are resolved against base_dir."""
        result = expand_command_path("sub/file.platy", tmp_path)
        assert result == tmp_path / "sub" / "file.platy"

    def test_tilde_expansion(self, tmp_path: Path) -> None:
        """Tilde is expanded to home directory."""
        result = expand_command_path("~/test.platy", tmp_path)
        assert str(result).startswith(str(Path.home()))
        assert result.name == "test.platy"

    def test_env_var_expansion(self, tmp_path: Path, monkeypatch) -> None:
        """Environment variables are expanded."""
        monkeypatch.setenv("TEST_DIR", "/custom/dir")
        result = expand_command_path("$TEST_DIR/test.platy", tmp_path)
        assert result == Path("/custom/dir/test.platy")
