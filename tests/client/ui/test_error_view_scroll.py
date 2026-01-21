#!/usr/bin/env python3
"""Unit tests for error view navigation and scrolling.

Tests the ErrorView navigate_up/navigate_down methods and line wrapping.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.error_view_wrap import wrap_error_lines


class TestLineWrapping:
    """Tests for line wrapping functionality."""

    def test_short_line_not_wrapped(self) -> None:
        """Lines shorter than width are not wrapped."""
        result = wrap_error_lines(["short"], 80)
        assert result == ["short"]

    def test_long_line_wrapped(self) -> None:
        """Lines longer than width are wrapped."""
        long_line = "a" * 100
        result = wrap_error_lines([long_line], 80)
        assert len(result) == 2
        assert result[0] == "a" * 80
        assert result[1] == "a" * 20

    def test_multiple_messages_wrapped(self) -> None:
        """Multiple messages are each wrapped."""
        messages = ["first", "a" * 100, "last"]
        result = wrap_error_lines(messages, 80)
        assert len(result) == 4
        assert result[0] == "first"
        assert result[3] == "last"

    def test_empty_message_preserved(self) -> None:
        """Empty messages produce empty line."""
        result = wrap_error_lines([""], 80)
        assert result == [""]

    def test_zero_width_returns_empty(self) -> None:
        """Zero width returns empty list."""
        result = wrap_error_lines(["test"], 0)
        assert result == []


class TestScrollBounds:
    """Tests for scroll boundary behavior."""

    def test_clamp_prevents_negative_offset(self) -> None:
        """Scroll offset cannot go negative."""
        from platyplaty.ui.error_view import ErrorView

        view = ErrorView([])
        view._scroll_offset = -5
        view._wrapped_lines = []
        view._clamp_scroll()
        assert view._scroll_offset == 0

    def test_navigate_up_at_top_is_noop(self) -> None:
        """Scroll up at top does nothing."""
        from platyplaty.ui.error_view import ErrorView

        view = ErrorView(["error1", "error2"])
        view._scroll_offset = 0
        view._wrapped_lines = ["error1", "error2"]
        view.navigate_up()
        assert view._scroll_offset == 0
