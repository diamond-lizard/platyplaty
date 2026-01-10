#!/usr/bin/env python3
"""Tests for path display fallback functions.

This module tests the fallback to full path components when the
abbreviated prefix exceeds the terminal width.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.path_abbreviation import (
    fallback_path_components,
    get_prefix_length,
    prefix_exceeds_width,
)
from platyplaty.ui.path_coloring import render_path_components
from platyplaty.ui.path_types import PathComponent, PathComponentType


class TestFallbackPathComponents:
    """Tests for fallback_path_components function."""

    def test_returns_full_components_from_root(self) -> None:
        """Fallback shows full path components from root that fit."""
        components = [
            PathComponent("/", PathComponentType.DIRECTORY, False),
            PathComponent("home", PathComponentType.DIRECTORY, False),
            PathComponent("user", PathComponentType.DIRECTORY, False),
            PathComponent("deeply", PathComponentType.DIRECTORY, False),
            PathComponent("nested", PathComponentType.DIRECTORY, False),
            PathComponent("file.milk", PathComponentType.FILE, True),
        ]
        result = fallback_path_components(components, max_width=10)
        names = [c.name for c in result]
        assert "/" in names
        assert "home" in names
        assert "file.milk" not in names

    def test_returns_just_root_when_nothing_else_fits(self) -> None:
        """When terminal is very narrow, return just root slash."""
        components = [
            PathComponent("/", PathComponentType.DIRECTORY, False),
            PathComponent("home", PathComponentType.DIRECTORY, False),
            PathComponent("file.milk", PathComponentType.FILE, True),
        ]
        result = fallback_path_components(components, max_width=1)
        assert len(result) == 1
        assert result[0].name == "/"

    def test_excludes_final_component(self) -> None:
        """The selected (final) component is never included in fallback."""
        components = [
            PathComponent("/", PathComponentType.DIRECTORY, False),
            PathComponent("home", PathComponentType.DIRECTORY, False),
            PathComponent("file.milk", PathComponentType.FILE, True),
        ]
        result = fallback_path_components(components, max_width=100)
        names = [c.name for c in result]
        assert "file.milk" not in names

    def test_empty_list_returns_empty(self) -> None:
        """Empty component list returns empty list."""
        result = fallback_path_components([], max_width=100)
        assert result == []

    def test_preserves_component_types(self) -> None:
        """Components in fallback retain their original types."""
        components = [
            PathComponent("/", PathComponentType.DIRECTORY, False),
            PathComponent("link", PathComponentType.SYMLINK, False),
            PathComponent("file.milk", PathComponentType.FILE, True),
        ]
        result = fallback_path_components(components, max_width=100)
        assert result[1].component_type == PathComponentType.SYMLINK


class TestPrefixExceedsWidth:
    """Tests for prefix_exceeds_width function."""

    def test_returns_true_when_prefix_too_wide(self) -> None:
        """Returns True when abbreviated prefix exceeds available width."""
        components = [
            PathComponent("/", PathComponentType.DIRECTORY, False),
            PathComponent("a", PathComponentType.DIRECTORY, False),
            PathComponent("b", PathComponentType.DIRECTORY, False),
            PathComponent("c", PathComponentType.DIRECTORY, False),
            PathComponent("d", PathComponentType.DIRECTORY, False),
            PathComponent("e", PathComponentType.DIRECTORY, False),
            PathComponent("f", PathComponentType.DIRECTORY, False),
            PathComponent("file.milk", PathComponentType.FILE, True),
        ]
        assert prefix_exceeds_width(components, max_width=5) is True

    def test_returns_true_when_less_than_2_chars_for_final(self) -> None:
        """Returns True when prefix leaves < 2 chars for final component."""
        components = [
            PathComponent("/", PathComponentType.DIRECTORY, False),
            PathComponent("home", PathComponentType.DIRECTORY, False),
            PathComponent("f.milk", PathComponentType.FILE, True),
        ]
        assert prefix_exceeds_width(components, max_width=3) is True

    def test_returns_false_when_sufficient_space(self) -> None:
        """Returns False when there is sufficient space."""
        components = [
            PathComponent("/", PathComponentType.DIRECTORY, False),
            PathComponent("home", PathComponentType.DIRECTORY, False),
            PathComponent("file.milk", PathComponentType.FILE, True),
        ]
        assert prefix_exceeds_width(components, max_width=100) is False

    def test_single_component_returns_false(self) -> None:
        """Single component (just root) returns False."""
        components = [PathComponent("/", PathComponentType.DIRECTORY, True)]
        assert prefix_exceeds_width(components, max_width=5) is False
