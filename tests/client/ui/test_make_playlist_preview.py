#!/usr/bin/env python3
"""Unit tests for make_playlist_preview function.

Tests the playlist preview creation for file browser right pane display.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.file_browser_playlist_preview import make_playlist_preview
from platyplaty.ui.file_browser_types import (
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

