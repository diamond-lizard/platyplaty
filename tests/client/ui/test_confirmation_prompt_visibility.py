#!/usr/bin/env python3
"""Unit tests for confirmation prompt visibility on Command Line.

Tests that confirmation prompt appears on Command Line when activated
and that Status Line remains visible during prompt activation.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.command_line import CommandLine
from platyplaty.ui.confirmation_prompt import ConfirmationPrompt


class TestConfirmationPromptOnCommandLine:
    """Tests that confirmation prompt appears on Command Line when activated."""

    def test_confirmation_prompt_is_child_of_command_line(self) -> None:
        """ConfirmationPrompt is yielded as child of CommandLine."""
        cmd_line = CommandLine()
        children = list(cmd_line.compose())
        types = [type(c) for c in children]
        assert ConfirmationPrompt in types

    def test_confirmation_prompt_has_display_none_by_default(self) -> None:
        """ConfirmationPrompt DEFAULT_CSS has display: none."""
        assert "display: none" in ConfirmationPrompt.DEFAULT_CSS

    def test_confirmation_prompt_visible_class_has_display_block(self) -> None:
        """ConfirmationPrompt .visible class has display: block."""
        assert "display: block" in ConfirmationPrompt.DEFAULT_CSS


class TestConfirmationPromptHiding:
    """Tests that Command Line returns to blank after prompt is dismissed."""

    def test_confirmation_prompt_hide_removes_visible_class(self) -> None:
        """ConfirmationPrompt._hide() removes the visible class."""
        import inspect
        source = inspect.getsource(ConfirmationPrompt._hide)
        assert "remove_class" in source
        assert "visible" in source


class TestStatusLineVisibleDuringConfirmation:
    """Tests that Status Line remains visible when confirmation prompt is active."""

    def test_status_line_does_not_yield_confirmation_prompt(self) -> None:
        """StatusLine does not yield ConfirmationPrompt as a child."""
        from platyplaty.ui.status_line import StatusLine
        status = StatusLine()
        children = list(status.compose())
        types = [type(c) for c in children]
        assert ConfirmationPrompt not in types

    def test_status_line_has_no_display_none(self) -> None:
        """StatusLine DEFAULT_CSS does not include display: none."""
        from platyplaty.ui.status_line import StatusLine
        assert "display: none" not in StatusLine.DEFAULT_CSS
