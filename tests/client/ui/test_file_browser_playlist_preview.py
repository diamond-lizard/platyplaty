#!/usr/bin/env python3
"""Tests for RightPanePlaylistPreview rendering.

This module tests rendering of playlist preview entries in the right pane,
including proper indentation, truncation, styling, and unfocused behavior.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.colors import BACKGROUND_COLOR, DIMMED_COLOR, FILE_COLOR
from platyplaty.ui.file_browser_right_pane_render import render_right_pane_line
from platyplaty.ui.file_browser_types import RightPanePlaylistPreview


class TestPlaylistPreviewRendering:
    """Tests for RightPanePlaylistPreview rendering."""

    def test_renders_entry_with_margins(self) -> None:
        """Entries render with 1-space left and right margins."""
        content = RightPanePlaylistPreview(names=("preset.milk",))
        result = render_right_pane_line(content, y=0, width=20)
        text = result[0].text
        assert text.startswith(" ")
        assert "preset.milk" in text

    def test_truncates_long_names(self) -> None:
        """Long names are truncated to fit content width."""
        content = RightPanePlaylistPreview(names=("very-long-preset-name.milk",))
        result = render_right_pane_line(content, y=0, width=15)
        text = result[0].text
        assert len(text) == 15
        assert "~" in text

    def test_white_on_black_styling(self) -> None:
        """Entries render with white foreground on black background."""
        content = RightPanePlaylistPreview(names=("preset.milk",))
        result = render_right_pane_line(content, y=0, width=20)
        assert result[0].style.color.name == FILE_COLOR
        assert result[0].style.bgcolor.name == BACKGROUND_COLOR

    def test_blank_line_beyond_entries(self) -> None:
        """Lines beyond entry count render as blank."""
        content = RightPanePlaylistPreview(names=("preset.milk",))
        result = render_right_pane_line(content, y=1, width=20)
        text = result[0].text
        assert text.strip() == ""
        assert len(text) == 20

    def test_dimmed_when_unfocused(self) -> None:
        """Entries render dimmed when unfocused."""
        content = RightPanePlaylistPreview(names=("preset.milk",))
        result = render_right_pane_line(content, y=0, width=20, focused=False)
        assert result[0].style.color.name == DIMMED_COLOR

    def test_multiple_entries_render_correctly(self) -> None:
        """Multiple entries each render at their respective y positions."""
        names = ("first.milk", "second.milk", "third.milk")
        content = RightPanePlaylistPreview(names=names)
        for i, name in enumerate(names):
            result = render_right_pane_line(content, y=i, width=20)
            text = result[0].text
            assert name in text

    def test_pads_to_full_width(self) -> None:
        """Entry text is padded to fill the pane width."""
        content = RightPanePlaylistPreview(names=("a.milk",))
        result = render_right_pane_line(content, y=0, width=30)
        text = result[0].text
        assert len(text) == 30
