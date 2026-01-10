#!/usr/bin/env python3
"""Tests for path component coloring.

This module tests path coloring functionality for the path display.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.colors import (
    BROKEN_SYMLINK_COLOR,
    DIRECTORY_COLOR,
    SELECTED_COLOR,
    SYMLINK_COLOR,
)
from platyplaty.ui.path_display import (
    _get_component_color,
    render_path_components,
)
from platyplaty.ui.path_types import PathComponent, PathComponentType


class TestComponentColor:
    """TASK-1900: Tests for color assignment for different component types."""

    def test_directory_color_is_blue(self) -> None:
        """Directory components get blue color."""
        comp = PathComponent("dir", PathComponentType.DIRECTORY, False)
        assert _get_component_color(comp) == DIRECTORY_COLOR

    def test_symlink_color_is_cyan(self) -> None:
        """Symlink components get cyan color."""
        comp = PathComponent("link", PathComponentType.SYMLINK, False)
        assert _get_component_color(comp) == SYMLINK_COLOR

    def test_broken_symlink_color_is_magenta(self) -> None:
        """TASK-2000: Broken symlink components get magenta color."""
        comp = PathComponent("dead", PathComponentType.BROKEN_SYMLINK, False)
        assert _get_component_color(comp) == BROKEN_SYMLINK_COLOR


class TestSelectedColor:
    """TASK-2300: Test selected item is bright white regardless of type."""

    def test_selected_directory_is_bright_white(self) -> None:
        """Selected directory is bright white, not blue."""
        comp = PathComponent("dir", PathComponentType.DIRECTORY, True)
        assert _get_component_color(comp) == SELECTED_COLOR

    def test_selected_symlink_is_bright_white(self) -> None:
        """Selected symlink is bright white, not cyan."""
        comp = PathComponent("link", PathComponentType.SYMLINK, True)
        assert _get_component_color(comp) == SELECTED_COLOR

    def test_selected_file_is_bright_white(self) -> None:
        """Selected file is bright white."""
        comp = PathComponent("file.milk", PathComponentType.FILE, True)
        assert _get_component_color(comp) == SELECTED_COLOR

    def test_selected_broken_symlink_is_bright_white(self) -> None:
        """Selected broken symlink is bright white, not magenta."""
        comp = PathComponent("dead", PathComponentType.BROKEN_SYMLINK, True)
        assert _get_component_color(comp) == SELECTED_COLOR


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
