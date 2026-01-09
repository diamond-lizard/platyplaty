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

from platyplaty.dispatch_tables import DispatchTable
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
