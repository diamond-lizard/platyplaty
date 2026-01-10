#!/usr/bin/env python3
"""Tests for path rendering orchestrator.

This module tests the orchestrator function that implements the
complete path rendering algorithm for the path display line.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.path_orchestrator import _render_components
from platyplaty.ui.path_types import PathComponent, PathComponentType


class TestRenderComponentsFullPath:
    """Tests for full path rendering when it fits."""

    def test_full_path_fits_returns_full_path(self) -> None:
        """When full path fits within width, return it unchanged."""
        components = [
            PathComponent("/", PathComponentType.DIRECTORY, False),
            PathComponent("home", PathComponentType.DIRECTORY, False),
            PathComponent("file.milk", PathComponentType.FILE, True),
        ]
        result = _render_components(components, width=100)
        assert result.plain == "/home/file.milk"

    def test_empty_components_returns_empty_text(self) -> None:
        """Empty component list returns empty Text."""
        result = _render_components([], width=100)
        assert result.plain == ""


class TestRenderComponentsAbbreviation:
    """Tests for path abbreviation when full path is too long."""

    def test_abbreviation_needed_abbreviates_path(self) -> None:
        """When full path too long but abbreviated fits, use abbreviated."""
        components = [
            PathComponent("/", PathComponentType.DIRECTORY, False),
            PathComponent("home", PathComponentType.DIRECTORY, False),
            PathComponent("user", PathComponentType.DIRECTORY, False),
            PathComponent("file.milk", PathComponentType.FILE, True),
        ]
        result = _render_components(components, width=15)
        assert result.plain == "/h/u/file.milk"


class TestRenderComponentsFallback:
    """Tests for fallback when abbreviated prefix exceeds width."""

    def test_fallback_when_prefix_too_wide(self) -> None:
        """When abbreviated prefix exceeds width, fall back to root components."""
        components = [
            PathComponent("/", PathComponentType.DIRECTORY, False),
            PathComponent("home", PathComponentType.DIRECTORY, False),
            PathComponent("a", PathComponentType.DIRECTORY, False),
            PathComponent("b", PathComponentType.DIRECTORY, False),
            PathComponent("c", PathComponentType.DIRECTORY, False),
            PathComponent("file.milk", PathComponentType.FILE, True),
        ]
        result = _render_components(components, width=6)
        assert "/" in result.plain
        assert "file.milk" not in result.plain


class TestRenderComponentsTruncation:
    """Tests for final component truncation."""

    def test_truncation_when_abbreviated_path_too_long(self) -> None:
        """When abbreviated path still too long, truncate final component."""
        components = [
            PathComponent("/", PathComponentType.DIRECTORY, False),
            PathComponent("home", PathComponentType.DIRECTORY, False),
            PathComponent("very-long-filename.milk", PathComponentType.FILE, True),
        ]
        result = _render_components(components, width=15)
        assert "~" in result.plain
        assert len(result.plain) <= 15
