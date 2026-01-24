#!/usr/bin/env python3
"""Unit tests for transient error behavior.

Tests that transient errors appear correctly on the Command Line
and return to blank after timeout.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.transient_error import TransientErrorBar


class TestTransientErrorAppearance:
    """Tests that transient errors appear on Command Line when triggered."""

    def test_transient_error_bar_hidden_by_default(self) -> None:
        """TransientErrorBar has display: none by default."""
        assert "display: none" in TransientErrorBar.DEFAULT_CSS

    def test_transient_error_bar_visible_class_shows_block(self) -> None:
        """TransientErrorBar.visible class sets display: block."""
        assert "display: block" in TransientErrorBar.DEFAULT_CSS

    def test_add_visible_class_makes_widget_visible(self) -> None:
        """Adding 'visible' class makes TransientErrorBar visible."""
        error_bar = TransientErrorBar()
        assert not error_bar.has_class("visible")
        error_bar.add_class("visible")
        assert error_bar.has_class("visible")

    def test_message_attribute_can_be_set(self) -> None:
        """TransientErrorBar.message can be set to error text."""
        error_bar = TransientErrorBar()
        assert error_bar.message == ""
        error_bar.message = "Test error message"
        assert error_bar.message == "Test error message"


class TestTransientErrorTimeout:
    """Tests that Command Line returns to blank after transient error timeout."""

    def test_hide_removes_visible_class(self) -> None:
        """TransientErrorBar._hide() removes the 'visible' class."""
        error_bar = TransientErrorBar()
        error_bar.add_class("visible")
        error_bar._hide()
        assert not error_bar.has_class("visible")

    def test_hide_clears_message(self) -> None:
        """TransientErrorBar._hide() clears the message attribute."""
        error_bar = TransientErrorBar()
        error_bar.message = "Some error"
        error_bar._hide()
        assert error_bar.message == ""

    def test_cancel_and_hide_removes_visible_class(self) -> None:
        """TransientErrorBar.cancel_and_hide() removes the 'visible' class."""
        error_bar = TransientErrorBar()
        error_bar.add_class("visible")
        error_bar.cancel_and_hide()
        assert not error_bar.has_class("visible")

    def test_cancel_and_hide_clears_message(self) -> None:
        """TransientErrorBar.cancel_and_hide() clears the message."""
        error_bar = TransientErrorBar()
        error_bar.message = "Some error"
        error_bar.cancel_and_hide()
        assert error_bar.message == ""
