#!/usr/bin/env python3
"""Error case tests for make_playlist_preview function.

Tests error handling: permission denied, file not found, and binary content.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.file_browser_playlist_preview import make_playlist_preview
from platyplaty.ui.file_browser_types import RightPaneBinaryFile


class TestPermissionDenied:
    """Tests for make_playlist_preview with permission denied."""

    def test_permission_denied_returns_none(self, tmp_path: Path) -> None:
        """Permission denied returns None."""
        browser = MagicMock()
        browser.current_dir = tmp_path
        entry = MagicMock()
        entry.name = "secret.platy"
        with patch("pathlib.Path.read_bytes") as mock_read:
            mock_read.side_effect = PermissionError()
            result = make_playlist_preview(browser, entry)
            assert result is None


class TestFileNotFound:
    """Tests for make_playlist_preview when file vanishes."""

    def test_file_not_found_returns_none(self, tmp_path: Path) -> None:
        """File not found (race condition) returns None."""
        browser = MagicMock()
        browser.current_dir = tmp_path
        entry = MagicMock()
        entry.name = "vanished.platy"
        result = make_playlist_preview(browser, entry)
        assert result is None


class TestBinaryContent:
    """Tests for make_playlist_preview with binary content."""

    def test_binary_returns_binary_file(self, tmp_path: Path) -> None:
        """Binary content returns RightPaneBinaryFile."""
        platy_file = tmp_path / "binary.platy"
        platy_file.write_bytes(b"\xff\xfe\x00\x01")
        browser = MagicMock()
        browser.current_dir = tmp_path
        entry = MagicMock()
        entry.name = "binary.platy"
        result = make_playlist_preview(browser, entry)
        assert isinstance(result, RightPaneBinaryFile)
