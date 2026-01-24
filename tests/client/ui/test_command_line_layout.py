#!/usr/bin/env python3
"""Unit tests for Command Line and Status Line layout independence.

Tests that Status Line remains visible independently of transient errors
and that transient errors are suppressed when prompts are active.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.command_line import CommandLine
from platyplaty.ui.command_prompt import CommandPrompt
from platyplaty.ui.confirmation_prompt import ConfirmationPrompt
from platyplaty.ui.transient_error import TransientErrorBar


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


class TestTransientErrorSuppression:
    """Tests that transient errors are suppressed when prompts are active."""

    def test_command_prompt_visible_class_in_css(self) -> None:
        """CommandPrompt CSS defines a .visible class."""
        assert "visible" in CommandPrompt.DEFAULT_CSS

    def test_confirmation_prompt_visible_class_in_css(self) -> None:
        """ConfirmationPrompt CSS defines a .visible class."""
        assert "visible" in ConfirmationPrompt.DEFAULT_CSS

    def test_command_line_checks_command_prompt_visible(self) -> None:
        """CommandLine.show_transient_error checks CommandPrompt visible class."""
        import inspect
        source = inspect.getsource(CommandLine.show_transient_error)
        assert "command_prompt" in source
        assert "has_class" in source
        assert "visible" in source

    def test_command_line_checks_confirmation_prompt_visible(self) -> None:
        """CommandLine.show_transient_error checks ConfirmationPrompt visible class."""
        import inspect
        source = inspect.getsource(CommandLine.show_transient_error)
        assert "confirmation_prompt" in source
        assert "has_class" in source
