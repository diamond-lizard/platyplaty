#!/usr/bin/env python3
"""Integration tests for make_file_preview delegation to playlist preview.

Tests that make_file_preview correctly delegates .platy files to
make_playlist_preview instead of treating them as generic text files.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.file_browser_file_preview import make_file_preview
from platyplaty.ui.file_browser_types import RightPanePlaylistPreview


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
