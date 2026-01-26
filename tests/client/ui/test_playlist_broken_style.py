#!/usr/bin/env python3
"""Unit tests for broken preset visual styling in playlist view.

Tests the _get_style() function from playlist_entry_render module
to verify correct styling for broken presets.
"""

import sys
from pathlib import Path

from rich.style import Style

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.playlist_entry_render import _get_style


class TestBrokenPresetStyling:
    """Tests for broken preset visual styling."""

    def test_broken_normal_shows_red_on_black(self) -> None:
        """Broken preset not selected shows red text on black background."""
        style = _get_style(is_selected=False, is_focused=True, is_broken=True)
        assert style.color.name == "red"
        assert style.bgcolor.name == "black"

    def test_broken_selected_focused_shows_black_on_red(self) -> None:
        """Broken preset selected and focused shows black text on red background."""
        style = _get_style(is_selected=True, is_focused=True, is_broken=True)
        assert style.color.name == "black"
        assert style.bgcolor.name == "red"

    def test_broken_selected_unfocused_shows_black_on_red(self) -> None:
        """Broken preset selected but unfocused shows black on red (not inverted)."""
        style = _get_style(is_selected=True, is_focused=False, is_broken=True)
        assert style.color.name == "black"
        assert style.bgcolor.name == "red"

    def test_broken_unfocused_shows_red_on_black(self) -> None:
        """Broken preset in unfocused pane shows red on black."""
        style = _get_style(is_selected=False, is_focused=False, is_broken=True)
        assert style.color.name == "red"
        assert style.bgcolor.name == "black"


class TestNormalPresetStyling:
    """Tests for normal (non-broken) preset styling for comparison."""

    def test_normal_selected_focused_shows_black_on_white(self) -> None:
        """Normal preset selected and focused shows black on white."""
        style = _get_style(is_selected=True, is_focused=True, is_broken=False)
        assert style.color.name == "black"
        assert style.bgcolor.name == "white"

    def test_normal_not_selected_focused_shows_white_on_black(self) -> None:
        """Normal preset not selected but focused shows white on black."""
        style = _get_style(is_selected=False, is_focused=True, is_broken=False)
        assert style.color.name == "white"
        assert style.bgcolor.name == "black"

    def test_normal_unfocused_shows_dimmed(self) -> None:
        """Normal preset in unfocused pane shows dimmed colors."""
        style = _get_style(is_selected=False, is_focused=False, is_broken=False)
        assert style.color.name == "bright_black"
