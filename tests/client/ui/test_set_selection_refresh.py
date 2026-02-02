#!/usr/bin/env python3
"""Tests for set_selection_by_index refreshing the right pane.

This module tests that set_selection_by_index calls _refresh_right_pane
to update the right pane content when the selection changes.
"""

import sys
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.file_browser import FileBrowser


class TestSetSelectionRefreshesRightPane:
    """Tests for set_selection_by_index calling _refresh_right_pane."""

    def test_set_selection_by_index_refreshes_right_pane(
        self, tmp_path: Path
    ) -> None:
        """set_selection_by_index calls _refresh_right_pane after update."""
        # Create directory with multiple files
        (tmp_path / "alpha.milk").write_text("alpha")
        (tmp_path / "beta.milk").write_text("beta")
        (tmp_path / "gamma.milk").write_text("gamma")

        browser = FileBrowser({}, starting_dir=tmp_path)

        with patch(
            "platyplaty.ui.file_browser._refresh_right_pane"
        ) as mock_refresh:
            browser.set_selection_by_index(1)
            mock_refresh.assert_called_once_with(browser)

    def test_set_selection_no_refresh_on_invalid_index(
        self, tmp_path: Path
    ) -> None:
        """set_selection_by_index does not refresh for invalid index."""
        (tmp_path / "alpha.milk").write_text("alpha")

        browser = FileBrowser({}, starting_dir=tmp_path)

        with patch(
            "platyplaty.ui.file_browser._refresh_right_pane"
        ) as mock_refresh:
            browser.set_selection_by_index(999)
            mock_refresh.assert_not_called()

    def test_set_selection_no_refresh_on_negative_index(
        self, tmp_path: Path
    ) -> None:
        """set_selection_by_index does not refresh for negative index."""
        (tmp_path / "alpha.milk").write_text("alpha")

        browser = FileBrowser({}, starting_dir=tmp_path)

        with patch(
            "platyplaty.ui.file_browser._refresh_right_pane"
        ) as mock_refresh:
            browser.set_selection_by_index(-1)
            mock_refresh.assert_not_called()
