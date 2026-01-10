#!/usr/bin/env python3
"""Tests for path truncation functions.

This module tests truncation of the final path component when
the abbreviated path still exceeds the terminal width.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.path_truncation import (
    truncate_abbreviated_path,
    truncate_final_component,
)
from platyplaty.ui.path_types import PathComponent, PathComponentType


class TestTruncateFinalComponent:
    """Tests for truncate_final_component function."""

    def test_no_truncation_when_fits(self) -> None:
        """Component is unchanged when it fits within max_length."""
        comp = PathComponent("short.milk", PathComponentType.FILE, True)
        result = truncate_final_component(comp, 20)
        assert result.name == "short.milk"

    def test_truncation_adds_tilde(self) -> None:
        """Truncated component ends with tilde indicator."""
        comp = PathComponent("very-long-preset-name.milk", PathComponentType.FILE, True)
        result = truncate_final_component(comp, 10)
        assert result.name.endswith("~")
        assert len(result.name) == 10

    def test_truncation_preserves_type(self) -> None:
        """Truncated component keeps its original type."""
        comp = PathComponent("long-name.milk", PathComponentType.FILE, True)
        result = truncate_final_component(comp, 5)
        assert result.component_type == PathComponentType.FILE

    def test_truncation_preserves_is_selected(self) -> None:
        """Truncated component keeps its is_selected flag."""
        comp = PathComponent("long-name.milk", PathComponentType.FILE, True)
        result = truncate_final_component(comp, 5)
        assert result.is_selected is True

    def test_minimum_display_one_char_plus_tilde(self) -> None:
        """Minimum display is one character plus tilde when max_length < 2."""
        comp = PathComponent("longname.milk", PathComponentType.FILE, True)
        result = truncate_final_component(comp, 1)
        assert result.name == "l~"
        assert len(result.name) == 2
