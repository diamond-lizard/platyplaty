#!/usr/bin/env python3
"""Tests for path abbreviation functionality.

This module tests path abbreviation for the path display.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.path_abbreviation import (
    abbreviate_component,
    abbreviate_path_components,
    get_rendered_length,
)
from platyplaty.ui.path_coloring import render_path_components
from platyplaty.ui.path_types import PathComponent, PathComponentType


class TestAbbreviateComponent:
    """Tests for abbreviate_component function."""

    def test_abbreviates_to_first_letter(self) -> None:
        """Component name is reduced to first letter only."""
        comp = PathComponent("presets", PathComponentType.DIRECTORY, False)
        result = abbreviate_component(comp)
        assert result.name == "p"

    @pytest.mark.parametrize("comp_type", [
        PathComponentType.DIRECTORY,
        PathComponentType.SYMLINK,
        PathComponentType.BROKEN_SYMLINK,
    ])
    def test_preserves_component_type(self, comp_type: PathComponentType) -> None:
        """Abbreviated component keeps its original type."""
        comp = PathComponent("name", comp_type, False)
        result = abbreviate_component(comp)
        assert result.component_type == comp_type

    def test_preserves_is_selected(self) -> None:
        """Abbreviated component keeps its is_selected flag."""
        comp = PathComponent("selected", PathComponentType.DIRECTORY, True)
        result = abbreviate_component(comp)
        assert result.is_selected is True

    def test_root_slash_unchanged(self) -> None:
        """Root slash is not abbreviated."""
        comp = PathComponent("/", PathComponentType.DIRECTORY, False)
        result = abbreviate_component(comp)
        assert result.name == "/"


class TestAbbreviatePathComponents:
    """Tests for abbreviate_path_components function."""

    def test_abbreviates_all_except_final(self) -> None:
        """All components except final are abbreviated to first letter."""
        components = [
            PathComponent("/", PathComponentType.DIRECTORY, False),
            PathComponent("home", PathComponentType.DIRECTORY, False),
            PathComponent("user", PathComponentType.DIRECTORY, False),
            PathComponent("presets", PathComponentType.DIRECTORY, False),
            PathComponent("cool-preset.milk", PathComponentType.FILE, True),
        ]
        result = abbreviate_path_components(components, max_width=10)
        assert result[0].name == "/"
        assert result[1].name == "h"
        assert result[2].name == "u"
        assert result[3].name == "p"
        assert result[4].name == "cool-preset.milk"

    def test_returns_original_when_fits(self) -> None:
        """Returns original components when path fits within width."""
        components = [
            PathComponent("/", PathComponentType.DIRECTORY, False),
            PathComponent("home", PathComponentType.DIRECTORY, False),
        ]
        result = abbreviate_path_components(components, max_width=100)
        assert result[1].name == "home"

    def test_empty_list_returns_empty(self) -> None:
        """Empty component list returns empty list."""
        result = abbreviate_path_components([], max_width=100)
        assert result == []


    def test_rendered_abbreviated_path_has_correct_colors(self) -> None:
        """Rendered abbreviated path shows correct colors for each component."""
        components = [
            PathComponent("/", PathComponentType.DIRECTORY, False),
            PathComponent("home", PathComponentType.DIRECTORY, False),
            PathComponent("link", PathComponentType.SYMLINK, False),
            PathComponent("file.milk", PathComponentType.FILE, True),
        ]
        abbreviated = abbreviate_path_components(components, max_width=10)
        rendered = render_path_components(abbreviated)
        spans = rendered.spans
        assert abbreviated[1].component_type == PathComponentType.DIRECTORY
        assert abbreviated[2].component_type == PathComponentType.SYMLINK
