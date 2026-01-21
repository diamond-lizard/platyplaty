#!/usr/bin/env python3
"""Tests for error indicator widget visibility.

This module tests that the ErrorIndicator widget shows/hides
correctly based on the error log state.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.error_indicator import (
    ERROR_INDICATOR_STYLE,
    ErrorIndicator,
)


class TestErrorIndicatorStyle:
    """Tests for error indicator styling constants."""

    def test_style_color_is_red(self) -> None:
        """Error indicator foreground should be red."""
        assert ERROR_INDICATOR_STYLE.color.name == "red"

    def test_style_bgcolor_is_black(self) -> None:
        """Error indicator background should be black."""
        assert ERROR_INDICATOR_STYLE.bgcolor.name == "black"


class TestErrorIndicatorVisibility:
    """Tests for error indicator visibility based on error log."""

    def test_visible_when_errors_exist(self) -> None:
        """Indicator should have visible class when error log is non-empty."""
        error_log: list[str] = ["Some error"]
        indicator = ErrorIndicator(error_log)
        indicator.update_visibility()
        assert "visible" in indicator.classes

    def test_hidden_when_no_errors(self) -> None:
        """Indicator should not have visible class when error log is empty."""
        error_log: list[str] = []
        indicator = ErrorIndicator(error_log)
        indicator.update_visibility()
        assert "visible" not in indicator.classes

    def test_becomes_visible_when_error_added(self) -> None:
        """Indicator should become visible when error is added to log."""
        error_log: list[str] = []
        indicator = ErrorIndicator(error_log)
        indicator.update_visibility()
        assert "visible" not in indicator.classes
        error_log.append("New error")
        indicator.update_visibility()
        assert "visible" in indicator.classes

    def test_becomes_hidden_when_errors_cleared(self) -> None:
        """Indicator should hide when errors are cleared."""
        error_log: list[str] = ["Error 1", "Error 2"]
        indicator = ErrorIndicator(error_log)
        indicator.update_visibility()
        assert "visible" in indicator.classes
        error_log.clear()
        indicator.update_visibility()
        assert "visible" not in indicator.classes
