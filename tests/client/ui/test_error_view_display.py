#!/usr/bin/env python3
"""Unit tests for error view display.

Tests the ErrorView widget rendering including header, footer,
empty state, and content display.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.error_view_render import (
    _render_header,
    _render_footer,
    _render_empty_state,
)


class TestHeader:
    """Tests for header rendering."""

    def test_header_contains_title(self) -> None:
        """Header contains 'Renderer Errors' text."""
        strip = _render_header(80)
        text = "".join(seg.text for seg in strip._segments)
        assert "Renderer Errors" in text

    def test_header_padded_to_width(self) -> None:
        """Header is padded to terminal width."""
        strip = _render_header(80)
        text = "".join(seg.text for seg in strip._segments)
        assert len(text) == 80


class TestFooter:
    """Tests for footer rendering."""

    def test_footer_contains_escape_hint(self) -> None:
        """Footer contains escape key hint."""
        strip = _render_footer(80)
        text = "".join(seg.text for seg in strip._segments)
        assert "Escape" in text

    def test_footer_contains_clear_hint(self) -> None:
        """Footer contains clear key hint."""
        strip = _render_footer(80)
        text = "".join(seg.text for seg in strip._segments)
        assert "c" in text

    def test_footer_padded_to_width(self) -> None:
        """Footer is padded to terminal width."""
        strip = _render_footer(80)
        text = "".join(seg.text for seg in strip._segments)
        assert len(text) == 80


class TestEmptyState:
    """Tests for empty state display."""

    def test_first_line_shows_no_errors(self) -> None:
        """First content line shows 'No errors' when empty."""
        strip = _render_empty_state(0, 80)
        text = "".join(seg.text for seg in strip._segments)
        assert "No errors" in text

    def test_subsequent_lines_empty(self) -> None:
        """Lines after first are blank when empty."""
        strip = _render_empty_state(1, 80)
        text = "".join(seg.text for seg in strip._segments)
        assert "No errors" not in text
        assert len(text) == 80
