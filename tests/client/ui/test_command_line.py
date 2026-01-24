#!/usr/bin/env python3
"""Unit tests for CommandLine widget.

Tests that the CommandLine widget renders correctly and yields
the expected child widgets.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.command_line import CommandLine
from platyplaty.ui.command_prompt import CommandPrompt
from platyplaty.ui.confirmation_prompt import ConfirmationPrompt
from platyplaty.ui.transient_error import TransientErrorBar


class TestCommandLineDefaultStyling:
    """Tests that CommandLine has correct default styling."""

    def test_default_css_has_black_background(self) -> None:
        """CommandLine DEFAULT_CSS includes black background."""
        assert "background: black" in CommandLine.DEFAULT_CSS

    def test_default_css_has_white_foreground(self) -> None:
        """CommandLine DEFAULT_CSS includes white foreground (color)."""
        assert "color: white" in CommandLine.DEFAULT_CSS


class TestCommandLineHeight:
    """Tests that CommandLine has height of 1 row."""

    def test_default_css_has_height_1(self) -> None:
        """CommandLine DEFAULT_CSS specifies height: 1."""
        assert "height: 1" in CommandLine.DEFAULT_CSS

    def test_default_css_docks_to_bottom(self) -> None:
        """CommandLine DEFAULT_CSS docks to bottom."""
        assert "dock: bottom" in CommandLine.DEFAULT_CSS


class TestCommandLineChildren:
    """Tests that CommandLine yields correct child widgets."""

    def test_compose_yields_command_prompt(self) -> None:
        """CommandLine compose yields a CommandPrompt widget."""
        widget = CommandLine()
        children = list(widget.compose())
        types = [type(c) for c in children]
        assert CommandPrompt in types

    def test_compose_yields_transient_error(self) -> None:
        """CommandLine compose yields a TransientErrorBar widget."""
        widget = CommandLine()
        children = list(widget.compose())
        types = [type(c) for c in children]
        assert TransientErrorBar in types

    def test_compose_yields_confirmation_prompt(self) -> None:
        """CommandLine compose yields a ConfirmationPrompt widget."""
        widget = CommandLine()
        children = list(widget.compose())
        types = [type(c) for c in children]
        assert ConfirmationPrompt in types

    def test_command_prompt_has_correct_id(self) -> None:
        """CommandPrompt child has ID 'command_prompt'."""
        widget = CommandLine()
        children = list(widget.compose())
        prompt = next(c for c in children if isinstance(c, CommandPrompt))
        assert prompt.id == "command_prompt"

    def test_transient_error_has_correct_id(self) -> None:
        """TransientErrorBar child has ID 'transient_error'."""
        widget = CommandLine()
        children = list(widget.compose())
        error_bar = next(c for c in children if isinstance(c, TransientErrorBar))
        assert error_bar.id == "transient_error"

    def test_confirmation_prompt_has_correct_id(self) -> None:
        """ConfirmationPrompt child has ID 'confirmation_prompt'."""
        widget = CommandLine()
        children = list(widget.compose())
        prompt = next(c for c in children if isinstance(c, ConfirmationPrompt))
        assert prompt.id == "confirmation_prompt"


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


class TestStatusLineIndependence:
    """Tests that Status Line remains visible when transient error is displayed."""

    def test_status_line_and_command_line_are_separate_widgets(self) -> None:
        """StatusLine and CommandLine are distinct widget classes."""
        from platyplaty.ui.status_line import StatusLine
        assert StatusLine is not CommandLine

    def test_both_widgets_dock_to_bottom(self) -> None:
        """Both StatusLine and CommandLine dock to bottom."""
        from platyplaty.ui.status_line import StatusLine
        assert "dock: bottom" in StatusLine.DEFAULT_CSS
        assert "dock: bottom" in CommandLine.DEFAULT_CSS

    def test_transient_error_is_child_of_command_line(self) -> None:
        """TransientErrorBar is yielded by CommandLine, not StatusLine."""
        cmd_line = CommandLine()
        children = list(cmd_line.compose())
        types = [type(c) for c in children]
        assert TransientErrorBar in types

    def test_status_line_does_not_yield_transient_error(self) -> None:
        """StatusLine does not yield TransientErrorBar as a child."""
        from platyplaty.ui.status_line import StatusLine
        status = StatusLine()
        children = list(status.compose())
        types = [type(c) for c in children]
        assert TransientErrorBar not in types
