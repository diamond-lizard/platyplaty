#!/usr/bin/env python3
"""Unit tests for persistent message widget.

Tests that PersistentMessage displays messages correctly and responds
to show_message/clear_message calls.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.persistent_message import PersistentMessage


class TestPersistentMessageShowMessage:
    """Tests for show_message method."""

    def test_show_message_sets_message_attribute(self) -> None:
        """show_message() sets the message attribute."""
        widget = PersistentMessage()
        widget.show_message("Command not found: 'foo'")
        assert widget.message == "Command not found: 'foo'"

    def test_show_message_adds_visible_class(self) -> None:
        """show_message() adds the 'visible' class."""
        widget = PersistentMessage()
        assert not widget.has_class("visible")
        widget.show_message("Test message")
        assert widget.has_class("visible")


class TestPersistentMessageClearMessage:
    """Tests for clear_message method."""

    def test_clear_message_clears_message_attribute(self) -> None:
        """clear_message() clears the message attribute."""
        widget = PersistentMessage()
        widget.message = "Some message"
        widget.add_class("visible")
        widget.clear_message()
        assert widget.message == ""

    def test_clear_message_removes_visible_class(self) -> None:
        """clear_message() removes the 'visible' class."""
        widget = PersistentMessage()
        widget.message = "Some message"
        widget.add_class("visible")
        widget.clear_message()
        assert not widget.has_class("visible")


class TestPersistentMessageRenderLine:
    """Tests for render_line method."""

    def test_render_line_returns_empty_strip_when_not_visible(self) -> None:
        """render_line() returns empty Strip when message is empty."""
        widget = PersistentMessage()
        strip = widget.render_line(0)
        assert len(strip) == 0

    def test_render_line_returns_empty_strip_for_wrong_line(self) -> None:
        """render_line() returns empty Strip for y != 0."""
        widget = PersistentMessage()
        widget.message = "Test message"
        strip = widget.render_line(1)
        assert len(strip) == 0


class TestPersistentMessageDefaultCSS:
    """Tests for DEFAULT_CSS configuration."""

    def test_hidden_by_default(self) -> None:
        """PersistentMessage has display: none by default."""
        assert "display: none" in PersistentMessage.DEFAULT_CSS

    def test_visible_class_shows_block(self) -> None:
        """PersistentMessage.visible class sets display: block."""
        assert "display: block" in PersistentMessage.DEFAULT_CSS

    def test_height_is_one_row(self) -> None:
        """PersistentMessage has height: 1."""
        assert "height: 1" in PersistentMessage.DEFAULT_CSS
