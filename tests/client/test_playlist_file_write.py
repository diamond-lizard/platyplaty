#!/usr/bin/env python3
"""Unit tests for playlist file writing.

Tests write_playlist_file() function.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.playlist_file import write_playlist_file
from platyplaty.playlist_validation import InvalidExtensionError


class TestWritePlaylistFile:
    """Tests for write_playlist_file function."""

    def test_write_valid_playlist(self, tmp_path: Path) -> None:
        """Write a valid playlist file."""
        filepath = tmp_path / "test.platy"
        presets = [Path("/home/user/a.milk"), Path("/opt/b.milk")]
        write_playlist_file(filepath, presets)
        content = filepath.read_text()
        assert "/home/user/a.milk" in content
        assert "/opt/b.milk" in content

    def test_write_empty_playlist(self, tmp_path: Path) -> None:
        """Write an empty playlist file."""
        filepath = tmp_path / "empty.platy"
        write_playlist_file(filepath, [])
        content = filepath.read_text()
        assert content == ""

    def test_write_invalid_extension_error(self, tmp_path: Path) -> None:
        """Non-.platy extension should raise InvalidExtensionError."""
        filepath = tmp_path / "test.txt"
        with pytest.raises(InvalidExtensionError) as exc_info:
            write_playlist_file(filepath, [])
        assert ".platy" in str(exc_info.value)

    def test_write_platy_case_insensitive(self, tmp_path: Path) -> None:
        """Extension validation should be case-insensitive."""
        filepath = tmp_path / "test.PLATY"
        presets = [Path("/home/user/a.milk")]
        write_playlist_file(filepath, presets)
        assert filepath.exists()

    def test_write_newline_separated(self, tmp_path: Path) -> None:
        """Entries should be newline-separated."""
        filepath = tmp_path / "test.platy"
        presets = [Path("/a.milk"), Path("/b.milk"), Path("/c.milk")]
        write_playlist_file(filepath, presets)
        lines = filepath.read_text().strip().split("\n")
        assert len(lines) == 3

    def test_write_trailing_newline(self, tmp_path: Path) -> None:
        """File should end with a trailing newline."""
        filepath = tmp_path / "test.platy"
        presets = [Path("/home/user/a.milk")]
        write_playlist_file(filepath, presets)
        content = filepath.read_text()
        assert content.endswith("\n")
