"""Tests for get_layout_state function.

Tests that the layout state is correctly determined based on the
right pane content type.
"""

import pytest

from platyplaty.ui.directory_types import DirectoryListing
from platyplaty.ui.file_browser_types import (
    RightPaneBinaryFile,
    RightPaneDirectory,
    RightPaneEmpty,
    RightPaneFilePreview,
    RightPaneNoMilk,
)
from platyplaty.ui.layout import LayoutState, get_layout_state


def test_standard_for_directory() -> None:
    """TASK-0900: get_layout_state returns STANDARD for RightPaneDirectory."""
    listing = DirectoryListing(entries=(), was_empty=False, had_filtered_entries=False, permission_denied=False)
    content = RightPaneDirectory(listing=listing)
    assert get_layout_state(content) == LayoutState.STANDARD


def test_standard_for_file_preview() -> None:
    """TASK-1000: get_layout_state returns STANDARD for RightPaneFilePreview."""
    content = RightPaneFilePreview(lines=("line 1", "line 2"))
    assert get_layout_state(content) == LayoutState.STANDARD


def test_standard_for_empty() -> None:
    """TASK-1100: get_layout_state returns STANDARD for RightPaneEmpty."""
    content = RightPaneEmpty()
    assert get_layout_state(content) == LayoutState.STANDARD


def test_standard_for_no_milk() -> None:
    """TASK-1200: get_layout_state returns STANDARD for RightPaneNoMilk."""
    content = RightPaneNoMilk()
    assert get_layout_state(content) == LayoutState.STANDARD


def test_standard_for_binary_file() -> None:
    """TASK-1300: get_layout_state returns STANDARD for RightPaneBinaryFile."""
    content = RightPaneBinaryFile()
    assert get_layout_state(content) == LayoutState.STANDARD


def test_stretched_for_none_broken_symlink() -> None:
    """TASK-1400: get_layout_state returns STRETCHED for None (broken symlink)."""
    assert get_layout_state(None) == LayoutState.STRETCHED


def test_stretched_for_none_inaccessible() -> None:
    """TASK-1500: get_layout_state returns STRETCHED for None (inaccessible)."""
    assert get_layout_state(None) == LayoutState.STRETCHED


def test_stretched_for_none_empty_file() -> None:
    """TASK-1600: get_layout_state returns STRETCHED for None (empty file)."""
    assert get_layout_state(None) == LayoutState.STRETCHED
