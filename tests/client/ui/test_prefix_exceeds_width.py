#!/usr/bin/env python3
"""Tests for prefix_exceeds_width function.

This module tests detection of when the abbreviated path prefix
exceeds the terminal width or leaves insufficient space for the
final component.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.path_fallback import prefix_exceeds_width
from platyplaty.ui.path_types import PathComponent, PathComponentType


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
