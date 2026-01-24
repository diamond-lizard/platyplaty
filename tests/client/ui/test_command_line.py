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

    def test_show_error_adds_visible_class(self) -> None:
        """TransientErrorBar.show_error() adds the 'visible' class."""
        error_bar = TransientErrorBar()
        error_bar.show_error("Test error")
        assert error_bar.has_class("visible")

    def test_show_error_sets_message(self) -> None:
        """TransientErrorBar.show_error() sets the message attribute."""
        error_bar = TransientErrorBar()
        error_bar.show_error("Test error message")
        assert error_bar.message == "Test error message"
