#!/usr/bin/env python3
"""Unit tests for playlist file I/O.

Tests parse_playlist_file(), parse_playlist_content(), and
write_playlist_file() functions.
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.playlist_file import (
    parse_playlist_content,
    parse_playlist_file,
    write_playlist_file,
)
from platyplaty.playlist_validation import (
    InvalidExtensionError,
    RelativePathError,
)


class TestParsePlaylistContent:
    """Tests for parse_playlist_content function."""

    def test_parse_valid_absolute_paths(self) -> None:
        """Parse content with valid absolute paths."""
        content = "/home/user/presets/cool.milk\n/opt/presets/nice.milk\n"
        result = parse_playlist_content(content)
        assert len(result) == 2
        assert result[0] == Path("/home/user/presets/cool.milk")
        assert result[1] == Path("/opt/presets/nice.milk")

    def test_parse_blank_lines_ignored(self) -> None:
        """Blank lines should be ignored."""
        content = "/home/user/a.milk\n\n\n/home/user/b.milk\n"
        result = parse_playlist_content(content)
        assert len(result) == 2

    def test_parse_whitespace_only_lines_ignored(self) -> None:
        """Lines with only whitespace should be ignored."""
        content = "/home/user/a.milk\n   \n\t\n/home/user/b.milk\n"
        result = parse_playlist_content(content)
        assert len(result) == 2

    def test_parse_tilde_expansion(self) -> None:
        """Tilde should be expanded to home directory."""
        content = "~/presets/cool.milk\n"
        result = parse_playlist_content(content)
        assert len(result) == 1
        assert result[0] == Path.home() / "presets" / "cool.milk"


    def test_parse_milk_case_insensitive(self) -> None:
        """Extension matching should be case-insensitive."""
        content = "/home/user/a.MILK\n/home/user/b.Milk\n/home/user/c.MiLk\n"
        result = parse_playlist_content(content)
        assert len(result) == 3

    def test_parse_empty_content(self) -> None:
        """Empty content should return empty list."""
        result = parse_playlist_content("")
        assert result == []
