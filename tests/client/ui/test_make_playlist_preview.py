#!/usr/bin/env python3
"""Unit tests for make_playlist_preview function.

Tests the playlist preview creation for file browser right pane display.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.file_browser_playlist_preview import make_playlist_preview
from platyplaty.ui.file_browser_file_preview import make_file_preview
from platyplaty.ui.file_browser_types import (
    RightPaneBinaryFile,
    RightPaneNoMilk,
    RightPanePlaylistPreview,
)


class TestValidFile:
    """Tests for make_playlist_preview with valid .platy files."""

    def test_valid_platy_returns_preview(self, tmp_path: Path) -> None:
        """Valid .platy file returns RightPanePlaylistPreview."""
        platy_file = tmp_path / "test.platy"
        platy_file.write_text("/home/user/a.milk\n/home/user/b.milk\n")
        browser = MagicMock()
        browser.current_dir = tmp_path
        entry = MagicMock()
        entry.name = "test.platy"
        result = make_playlist_preview(browser, entry)
        assert isinstance(result, RightPanePlaylistPreview)
        assert result.names == ("a.milk", "b.milk")


class TestEmptyFile:
    """Tests for make_playlist_preview with empty files."""

    def test_empty_file_returns_no_milk(self, tmp_path: Path) -> None:
        """Empty file returns RightPaneNoMilk."""
        platy_file = tmp_path / "empty.platy"
        platy_file.write_text("")
        browser = MagicMock()
        browser.current_dir = tmp_path
        entry = MagicMock()
        entry.name = "empty.platy"
        result = make_playlist_preview(browser, entry)
        assert isinstance(result, RightPaneNoMilk)


class TestAllInvalidLines:
    """Tests for make_playlist_preview with all invalid lines."""

    def test_all_invalid_returns_no_milk(self, tmp_path: Path) -> None:
        """File with all invalid lines returns RightPaneNoMilk."""
        platy_file = tmp_path / "invalid.platy"
        platy_file.write_text("relative.milk\n./local.milk\n")
        browser = MagicMock()
        browser.current_dir = tmp_path
        entry = MagicMock()
        entry.name = "invalid.platy"
        result = make_playlist_preview(browser, entry)
        assert isinstance(result, RightPaneNoMilk)


class TestDuplicateFilenames:
    """Tests for make_playlist_preview with duplicate filenames."""

    def test_duplicates_disambiguated(self, tmp_path: Path) -> None:
        """Duplicate filenames are disambiguated."""
        platy_file = tmp_path / "dups.platy"
        platy_file.write_text("/a/b/x.milk\n/a/c/x.milk\n")
        browser = MagicMock()
        browser.current_dir = tmp_path
        entry = MagicMock()
        entry.name = "dups.platy"
        result = make_playlist_preview(browser, entry)
        assert isinstance(result, RightPanePlaylistPreview)
        assert result.names == ("b/x.milk", "c/x.milk")


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


class TestMakeFilePreviewDelegation:
    """Integration tests for make_file_preview delegating to make_playlist_preview."""

    def test_platy_lowercase_delegates(self, tmp_path: Path) -> None:
        """make_file_preview delegates .platy files to make_playlist_preview."""
        platy_file = tmp_path / "test.platy"
        platy_file.write_text("/home/user/a.milk\n")
        browser = MagicMock()
        browser.current_dir = tmp_path
        browser.size = MagicMock()
        browser.size.height = 20
        entry = MagicMock()
        entry.name = "test.platy"
        result = make_file_preview(browser, entry)
        assert isinstance(result, RightPanePlaylistPreview)
        assert result.names == ("a.milk",)

    def test_platy_uppercase_delegates(self, tmp_path: Path) -> None:
        """make_file_preview delegates .PLATY files to make_playlist_preview."""
        platy_file = tmp_path / "test.PLATY"
        platy_file.write_text("/home/user/b.milk\n")
        browser = MagicMock()
        browser.current_dir = tmp_path
        browser.size = MagicMock()
        browser.size.height = 20
        entry = MagicMock()
        entry.name = "test.PLATY"
        result = make_file_preview(browser, entry)
        assert isinstance(result, RightPanePlaylistPreview)
        assert result.names == ("b.milk",)
