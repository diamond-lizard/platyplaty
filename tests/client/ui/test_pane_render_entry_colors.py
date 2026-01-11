#!/usr/bin/env python3
"""Tests for pane rendering entry color styling.

This module tests that render_pane_line() applies correct colors
to the returned Segments for different entry types.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.colors import (
    BACKGROUND_COLOR,
    BROKEN_SYMLINK_COLOR,
    DIRECTORY_COLOR,
    FILE_COLOR,
    SYMLINK_COLOR,
)
from platyplaty.ui.directory_types import DirectoryEntry, DirectoryListing, EntryType
from platyplaty.ui.file_browser_pane_render import render_pane_line


def _make_listing(entry: DirectoryEntry) -> DirectoryListing:
    """Create a simple listing with one entry."""
    return DirectoryListing(
        entries=[entry],
        was_empty=False,
        had_filtered_entries=False,
        permission_denied=False,
    )


class TestRenderPaneLineColors:
    """Tests for render_pane_line() color styling."""

    def test_directory_entry_has_blue_foreground(self) -> None:
        """Directory entries should render with blue foreground."""
        entry = DirectoryEntry(name="mydir", entry_type=EntryType.DIRECTORY, path=Path("/dummy"))
        result = render_pane_line(_make_listing(entry), y=0, width=20, is_left_pane=False)
        assert len(result) == 1
        assert result[0].style.color.name == DIRECTORY_COLOR

    def test_file_entry_has_white_foreground(self) -> None:
        """File entries should render with white foreground."""
        entry = DirectoryEntry(name="test.milk", entry_type=EntryType.FILE, path=Path("/dummy"))
        result = render_pane_line(_make_listing(entry), y=0, width=20, is_left_pane=False)
        assert len(result) == 1
        assert result[0].style.color.name == FILE_COLOR

    def test_symlink_to_dir_has_cyan_foreground(self) -> None:
        """Symlink-to-directory entries should render with cyan foreground."""
        entry = DirectoryEntry(name="link", entry_type=EntryType.SYMLINK_TO_DIRECTORY, path=Path("/dummy"))
        result = render_pane_line(_make_listing(entry), y=0, width=20, is_left_pane=False)
        assert len(result) == 1
        assert result[0].style.color.name == SYMLINK_COLOR

    def test_symlink_to_file_has_cyan_foreground(self) -> None:
        """Symlink-to-file entries should render with cyan foreground."""
        entry = DirectoryEntry(name="link.milk", entry_type=EntryType.SYMLINK_TO_FILE, path=Path("/dummy"))
        result = render_pane_line(_make_listing(entry), y=0, width=20, is_left_pane=False)
        assert len(result) == 1
        assert result[0].style.color.name == SYMLINK_COLOR

    def test_broken_symlink_has_magenta_foreground(self) -> None:
        """Broken symlink entries should render with magenta foreground."""
        entry = DirectoryEntry(name="broken", entry_type=EntryType.BROKEN_SYMLINK, path=Path("/dummy"))
        result = render_pane_line(_make_listing(entry), y=0, width=20, is_left_pane=False)
        assert len(result) == 1
        assert result[0].style.color.name == BROKEN_SYMLINK_COLOR

    def test_all_entries_have_black_background(self) -> None:
        """All entry types should have black background."""
        entry = DirectoryEntry(name="mydir", entry_type=EntryType.DIRECTORY, path=Path("/dummy"))
        result = render_pane_line(_make_listing(entry), y=0, width=20, is_left_pane=False)
        assert len(result) == 1
        assert result[0].style.bgcolor.name == BACKGROUND_COLOR
