#!/usr/bin/env python3
"""Unit tests for style utility functions."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from rich.style import Style

from platyplaty.ui.style_utils import reverse_style


class TestReverseStyle:
    """Tests for reverse_style function."""

    def test_swaps_colors(self):
        """Foreground and background colors are swapped."""
        style = Style(color="white", bgcolor="black")
        result = reverse_style(style)
        assert result.color.name == "black"
        assert result.bgcolor.name == "white"

    def test_handles_none_foreground(self):
        """None foreground is preserved as None."""
        style = Style(bgcolor="blue")
        result = reverse_style(style)
        assert result.color.name == "blue"
        assert result.bgcolor is None

    def test_handles_none_background(self):
        """None background is preserved as None."""
        style = Style(color="red")
        result = reverse_style(style)
        assert result.color is None
        assert result.bgcolor.name == "red"

    def test_both_none(self):
        """Both None returns empty style."""
        style = Style()
        result = reverse_style(style)
        assert result.color is None
        assert result.bgcolor is None
