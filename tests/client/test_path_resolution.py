#!/usr/bin/env python3
"""Unit tests for path argument resolution.

Tests _resolve_path_argument function for various path inputs.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.errors import StartupError
from platyplaty.run_sequence import _resolve_path_argument


class TestResolvePathArgument:
    """Tests for _resolve_path_argument function."""

    def test_none_returns_cwd(self) -> None:
        """None path returns current working directory."""
        result = _resolve_path_argument(None)
        assert result.start_directory == Path.cwd()
        assert result.playlist_path is None

    def test_directory_path(self, tmp_path: Path) -> None:
        """Directory path sets start_directory to that path."""
        result = _resolve_path_argument(str(tmp_path))
        assert result.start_directory == tmp_path
        assert result.playlist_path is None

    def test_platy_file_path(self, tmp_path: Path) -> None:
        """Platy file sets playlist_path and start_directory to parent."""
        playlist_file = tmp_path / "test.platy"
        playlist_file.touch()
        result = _resolve_path_argument(str(playlist_file))
        assert result.start_directory == tmp_path
        assert result.playlist_path == playlist_file

    def test_platy_extension_case_insensitive(self, tmp_path: Path) -> None:
        """Platy extension should be case-insensitive."""
        playlist_file = tmp_path / "test.PLATY"
        playlist_file.touch()
        result = _resolve_path_argument(str(playlist_file))
        assert result.playlist_path == playlist_file

    def test_nonexistent_path_raises_error(self) -> None:
        """Non-existent path raises StartupError."""
        with pytest.raises(StartupError) as exc_info:
            _resolve_path_argument("/nonexistent/path")
        assert "does not exist" in str(exc_info.value)

    def test_non_platy_file_raises_error(self, tmp_path: Path) -> None:
        """File without .platy extension raises StartupError."""
        other_file = tmp_path / "test.txt"
        other_file.touch()
        with pytest.raises(StartupError) as exc_info:
            _resolve_path_argument(str(other_file))
        assert ".platy extension" in str(exc_info.value)

    def test_milk_file_raises_error(self, tmp_path: Path) -> None:
        """Milk file raises StartupError (only .platy allowed)."""
        milk_file = tmp_path / "preset.milk"
        milk_file.touch()
        with pytest.raises(StartupError) as exc_info:
            _resolve_path_argument(str(milk_file))
        assert ".platy extension" in str(exc_info.value)
