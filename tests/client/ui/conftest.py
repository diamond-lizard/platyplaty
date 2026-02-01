#!/usr/bin/env python3
"""Shared pytest fixtures for UI navigation tests.

This module provides common fixtures used across the navigation test
files, including temporary directory trees and NavigationState instances.
"""

import sys
from pathlib import Path
from typing import Generator

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from unittest.mock import MagicMock

from platyplaty.dispatch_tables import DispatchTable
from platyplaty.ui.directory_types import DirectoryListing
from platyplaty.ui.nav_state import NavigationState


@pytest.fixture
def empty_dispatch_table() -> DispatchTable:
    """Provide an empty dispatch table for FileBrowser initialization.

    Returns:
        An empty dictionary as a DispatchTable.
    """
    return {}


@pytest.fixture
def temp_dir_tree(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary directory tree for testing.

    Creates a structure with:
    - presets/ directory containing .milk files
    - subdir/ subdirectory
    - Several .milk files at the root

    Args:
        tmp_path: Pytest's tmp_path fixture.

    Yields:
        Path to the root of the temporary directory tree.
    """
    # Create directories
    presets = tmp_path / "presets"
    presets.mkdir()
    subdir = tmp_path / "subdir"
    subdir.mkdir()

    # Create .milk files at root
    (tmp_path / "alpha.milk").write_text("alpha content")
    (tmp_path / "beta.milk").write_text("beta content")
    (tmp_path / "gamma.milk").write_text("gamma content")

    # Create .milk files in presets/
    (presets / "preset1.milk").write_text("preset1 content")
    (presets / "preset2.milk").write_text("preset2 content")

    yield tmp_path


@pytest.fixture
def nav_state(temp_dir_tree: Path) -> Generator[NavigationState, None, None]:
    """Create a NavigationState initialized to the temp directory tree.

    Args:
        temp_dir_tree: The temporary directory tree fixture.

    Yields:
        NavigationState initialized to the temp directory root.
    """
    state = NavigationState(temp_dir_tree)
    yield state

def make_listing(entries: list) -> DirectoryListing:
    """Create a DirectoryListing from a list of entries."""
    return DirectoryListing(
        entries=entries,
        was_empty=False,
        had_filtered_entries=False,
        permission_denied=False,
    )


@pytest.fixture
def mock_browser() -> MagicMock:
    """Create a mock FileBrowser for testing.

    The mock is configured so that calling set_selection_by_index(idx)
    updates browser.selected_index to idx. This mirrors the real
    FileBrowser behavior where selected_index is a read-only property
    derived from internal state that set_selection_by_index() modifies.
    Without this side_effect, tests that assert on selected_index after
    calling actions like action_play_next_preset() would fail because
    MagicMock doesn't automatically connect method calls to attributes.
    """
    browser = MagicMock()
    browser.app = MagicMock()
    browser.app.ctx = MagicMock()
    browser.app.ctx.playlist = MagicMock()
    browser.app.ctx.autoplay_manager = MagicMock()
    browser._adjust_scroll = MagicMock()
    browser.refresh = MagicMock()
    browser.set_selection_by_index = MagicMock(
        side_effect=lambda idx: setattr(browser, 'selected_index', idx)
    )
    return browser


class TestPrompt:
    """Fake implementation of PromptInterface for testing.

    This provides predictable behavior without mock configuration,
    following the "Don't Mock What You Don't Own" principle.
    """

    def __init__(self) -> None:
        """Initialize with empty input and cursor at position 0."""
        self.input_text: str = ""
        self.cursor_index: int = 0
        self.callback = None
        self.hidden: bool = False
        self.paste_result: bool = False

    def update_cursor_with_scroll(self, new_cursor: int) -> None:
        """Update cursor position."""
        self.cursor_index = new_cursor

    def hide(self) -> None:
        """Mark the prompt as hidden."""
        self.hidden = True

    def paste_from_selection(self) -> bool:
        """Return the configured paste result."""
        return self.paste_result


@pytest.fixture
def test_prompt() -> TestPrompt:
    """Provide a fresh TestPrompt instance for testing.

    Returns:
        A new TestPrompt with default empty state.
    """
    return TestPrompt()
