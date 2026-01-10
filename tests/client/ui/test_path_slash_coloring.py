#!/usr/bin/env python3
"""Tests for path slash coloring.

This module tests slash coloring functionality for the path display.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.colors import (
    DIRECTORY_COLOR,
    SYMLINK_COLOR,
)
from platyplaty.ui.path_coloring import render_path_components
from platyplaty.ui.path_types import PathComponent, PathComponentType


class TestSlashColoring:
    """TASK-2100, TASK-2200: Tests for slash coloring."""

    def test_leading_slash_colored_as_root(self) -> None:
        """TASK-2200: Leading slash is colored based on root type (blue)."""
        components = [
            PathComponent("/", PathComponentType.DIRECTORY, False),
            PathComponent("home", PathComponentType.DIRECTORY, True),
        ]
        result = render_path_components(components)
        spans = list(result.spans)
        assert len(spans) >= 1
        assert spans[0].style == DIRECTORY_COLOR

    def test_slash_after_directory_is_blue(self) -> None:
        """Slash after directory matches directory color (blue)."""
        components = [
            PathComponent("/", PathComponentType.DIRECTORY, False),
            PathComponent("home", PathComponentType.DIRECTORY, False),
            PathComponent("user", PathComponentType.DIRECTORY, True),
        ]
        result = render_path_components(components)
        plain = result.plain
        assert plain == "/home/user"

    def test_slash_after_symlink_is_cyan(self) -> None:
        """Slash after symlink matches symlink color (cyan)."""
        components = [
            PathComponent("/", PathComponentType.DIRECTORY, False),
            PathComponent("link", PathComponentType.SYMLINK, False),
            PathComponent("target", PathComponentType.DIRECTORY, True),
        ]
        result = render_path_components(components)
        spans = list(result.spans)
        slash_spans = [s for s in spans if result.plain[s.start:s.end] == "/"]
        assert len(slash_spans) >= 2
        assert slash_spans[1].style == SYMLINK_COLOR
