#!/usr/bin/env python3
"""Unit tests for status line error indicator.

Tests that the error indicator ("E") is shown at the right edge
of the status line when errors exist in the error log.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.status_line_render import render_status_line


class MockStatusLine:
    """Mock StatusLine widget for testing render function."""

    def __init__(
        self,
        error_log: list[str],
        autoplay: bool = False,
        filename: Path | None = None,
        dirty: bool = False,
    ) -> None:
        """Initialize mock with test state."""
        self._error_log = error_log
        self._autoplay_enabled = autoplay
        self._playlist_filename = filename
        self._dirty = dirty


class TestErrorIndicatorPresence:
    """Tests for error indicator visibility."""

    def test_shows_e_when_errors_exist(self) -> None:
        """Shows E at right edge when error log is non-empty."""
        error_log = ["some error"]
        widget = MockStatusLine(error_log)
        strip = render_status_line(widget, 80)
        text = "".join(seg.text for seg in strip)
        assert text.endswith("E")

    def test_no_e_when_no_errors(self) -> None:
        """Does not show E when error log is empty."""
        error_log: list[str] = []
        widget = MockStatusLine(error_log)
        strip = render_status_line(widget, 80)
        text = "".join(seg.text for seg in strip)
        assert not text.endswith("E")
