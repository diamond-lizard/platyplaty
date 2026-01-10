#!/usr/bin/env python3
"""Tests for abbreviate_component function.

This module tests single path component abbreviation for the path display.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.path_abbreviation import abbreviate_component
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
