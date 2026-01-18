#!/usr/bin/env python3
"""Unit tests for playlist file error handling.

Tests error conditions in parse_playlist_content().
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.playlist_file import parse_playlist_content
from platyplaty.playlist_validation import (
    InvalidExtensionError,
    RelativePathError,
)


class TestParsePlaylistErrors:
    """Tests for parse_playlist_content error handling."""

    def test_parse_relative_path_error(self) -> None:
        """Relative paths should raise RelativePathError."""
        content = "relative/path.milk\n"
        with pytest.raises(RelativePathError) as exc_info:
            parse_playlist_content(content)
        assert "line 1" in str(exc_info.value)

    def test_parse_dot_relative_path_error(self) -> None:
        """Paths starting with . should raise RelativePathError."""
        content = "./relative/path.milk\n"
        with pytest.raises(RelativePathError) as exc_info:
            parse_playlist_content(content)
        assert "line 1" in str(exc_info.value)

    def test_parse_dotdot_relative_path_error(self) -> None:
        """Paths starting with .. should raise RelativePathError."""
        content = "../relative/path.milk\n"
        with pytest.raises(RelativePathError) as exc_info:
            parse_playlist_content(content)
        assert "line 1" in str(exc_info.value)

    def test_parse_non_milk_extension_error(self) -> None:
        """Non-.milk extensions should raise InvalidExtensionError."""
        content = "/home/user/preset.txt\n"
        with pytest.raises(InvalidExtensionError) as exc_info:
            parse_playlist_content(content)
        assert "lines 1" in str(exc_info.value)

    def test_parse_multiple_non_milk_lists_all_lines(self) -> None:
        """Multiple non-.milk should list all line numbers."""
        content = "/home/user/a.txt\n/home/user/b.milk\n/home/user/c.mp3\n"
        with pytest.raises(InvalidExtensionError) as exc_info:
            parse_playlist_content(content)
        error_msg = str(exc_info.value)
        assert "1" in error_msg
        assert "3" in error_msg
