#!/usr/bin/env python3
"""Unit tests for _parse_playlist_tolerant function.

Tests the tolerant playlist parsing for file browser right pane preview.
"""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.file_browser_playlist_preview import _parse_playlist_tolerant


class TestValidPaths:
    """Tests for _parse_playlist_tolerant with valid paths only."""

    def test_valid_absolute_paths(self) -> None:
        """Valid absolute .milk paths are parsed."""
        content = "/home/user/presets/cool.milk\n/opt/viz/nice.milk\n"
        result = _parse_playlist_tolerant(content)
        assert len(result) == 2
        assert result[0] == Path("/home/user/presets/cool.milk")
        assert result[1] == Path("/opt/viz/nice.milk")


class TestMixedLines:
    """Tests for _parse_playlist_tolerant with mixed valid/invalid."""

    def test_mixed_valid_invalid(self) -> None:
        """Valid paths kept, invalid skipped."""
        content = "/valid/path.milk\nrelative.milk\n/another/valid.milk\n"
        result = _parse_playlist_tolerant(content)
        assert len(result) == 2
        assert result[0] == Path("/valid/path.milk")
        assert result[1] == Path("/another/valid.milk")


class TestBlankLines:
    """Tests for _parse_playlist_tolerant with blank lines."""

    def test_blank_lines_skipped(self) -> None:
        """Blank and whitespace-only lines are skipped."""
        content = "/valid.milk\n\n   \n\t\n/another.milk\n"
        result = _parse_playlist_tolerant(content)
        assert len(result) == 2


class TestAllInvalid:
    """Tests for _parse_playlist_tolerant with all invalid lines."""

    def test_all_invalid_returns_empty(self) -> None:
        """All invalid lines returns empty list."""
        content = "relative.milk\n./local.milk\nno-extension\n"
        result = _parse_playlist_tolerant(content)
        assert result == []


class TestRelativePaths:
    """Tests for _parse_playlist_tolerant with relative paths."""

    def test_relative_paths_skipped(self) -> None:
        """Relative paths are skipped."""
        content = "relative.milk\n./local.milk\n../parent.milk\n"
        result = _parse_playlist_tolerant(content)
        assert result == []


class TestExtensions:
    """Tests for _parse_playlist_tolerant with non-.milk extensions."""

    def test_non_milk_extensions_skipped(self) -> None:
        """Non-.milk extensions are skipped."""
        content = "/path/file.txt\n/path/file.mp3\n/path/valid.milk\n"
        result = _parse_playlist_tolerant(content)
        assert len(result) == 1
        assert result[0] == Path("/path/valid.milk")


class TestTildePaths:
    """Tests for _parse_playlist_tolerant with tilde paths."""

    def test_tilde_paths_expanded(self) -> None:
        """Tilde paths are expanded."""
        content = "~/presets/cool.milk\n"
        result = _parse_playlist_tolerant(content)
        assert len(result) == 1
        assert result[0] == Path.home() / "presets" / "cool.milk"


class TestInvalidUsername:
    """Tests for _parse_playlist_tolerant with invalid ~username."""

    def test_invalid_username_skipped(self) -> None:
        """Invalid ~username paths are silently skipped."""
        with patch(
            "platyplaty.ui.file_browser_playlist_preview.expand_path"
        ) as mock_expand:
            mock_expand.side_effect = RuntimeError("user not found")
            content = "~nonexistentuser/foo.milk\n"
            result = _parse_playlist_tolerant(content)
            assert result == []
