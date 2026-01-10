#!/usr/bin/env python3
"""Tests for pane rendering special case color styling.

This module tests empty/inaccessible message styling and file preview colors.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.colors import (
    BACKGROUND_COLOR,
    EMPTY_MESSAGE_BG,
    EMPTY_MESSAGE_FG,
    FILE_COLOR,
)
from platyplaty.ui.directory_types import DirectoryListing
from platyplaty.ui.file_browser_pane_render import render_pane_line, render_right_pane_line
from platyplaty.ui.file_browser_types import RightPaneFilePreview


class TestEmptyListingColors:
    """Tests for empty/inaccessible directory message styling."""

    def test_inaccessible_message_has_white_on_red(self) -> None:
        """Inaccessible directory message should be white on red."""
        listing = DirectoryListing(
            entries=[],
            was_empty=False,
            had_filtered_entries=False,
            permission_denied=True,
        )
        result = render_pane_line(listing, y=0, width=30, is_left_pane=False)
        assert len(result) == 1
        assert result[0].style.color.name == EMPTY_MESSAGE_FG
        assert result[0].style.bgcolor.name == EMPTY_MESSAGE_BG

    def test_empty_message_has_white_on_red(self) -> None:
        """Empty directory message should be white on red."""
        listing = DirectoryListing(
            entries=[],
            was_empty=True,
            had_filtered_entries=False,
            permission_denied=False,
        )
        result = render_pane_line(listing, y=0, width=20, is_left_pane=False)
        assert len(result) == 1
        assert result[0].style.color.name == EMPTY_MESSAGE_FG
        assert result[0].style.bgcolor.name == EMPTY_MESSAGE_BG

    def test_no_milk_files_message_has_white_on_red(self) -> None:
        """'no .milk files' message should be white on red."""
        listing = DirectoryListing(
            entries=[],
            was_empty=False,
            had_filtered_entries=True,
            permission_denied=False,
        )
        result = render_pane_line(listing, y=0, width=20, is_left_pane=False)
        assert len(result) == 1
        assert result[0].style.color.name == EMPTY_MESSAGE_FG
        assert result[0].style.bgcolor.name == EMPTY_MESSAGE_BG


class TestFilePreviewColors:
    """Tests for file preview content styling."""

    def test_file_preview_has_white_foreground(self) -> None:
        """File preview content should render with white foreground."""
        content = RightPaneFilePreview(lines=("line 1", "line 2"))
        result = render_right_pane_line(content, y=0, width=20)
        assert len(result) == 1
        assert result[0].style.color.name == FILE_COLOR

    def test_file_preview_has_black_background(self) -> None:
        """File preview content should have black background."""
        content = RightPaneFilePreview(lines=("line 1",))
        result = render_right_pane_line(content, y=0, width=20)
        assert len(result) == 1
        assert result[0].style.bgcolor.name == BACKGROUND_COLOR
