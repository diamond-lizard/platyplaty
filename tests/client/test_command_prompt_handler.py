#!/usr/bin/env python3
"""Unit tests for command prompt handler.

Tests that command execution failures correctly hide the prompt and show
persistent messages.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.command_prompt_handler import (
    create_command_callback,
    parse_command_input,
    show_command_error,
)


class TestParseCommandInput:
    """Tests for parse_command_input function."""

    def test_command_only(self) -> None:
        """Parse command with no arguments."""
        name, args = parse_command_input("load")
        assert name == "load"
        assert args is None

    def test_command_with_args(self) -> None:
        """Parse command with arguments."""
        name, args = parse_command_input("load /path/to/file.platy")
        assert name == "load"
        assert args == "/path/to/file.platy"


class TestShowCommandError:
    """Tests for show_command_error function."""

    def test_shows_persistent_message(self) -> None:
        """show_command_error calls show_persistent_message."""
        mock_app = MagicMock()
        mock_cmd_line = MagicMock()
        mock_app.query_one.return_value = mock_cmd_line

        show_command_error(mock_app, "Command not found: 'foo'")

        mock_cmd_line.show_persistent_message.assert_called_once_with(
            "Command not found: 'foo'"
        )

    def test_default_error_message(self) -> None:
        """show_command_error uses default message when error is None."""
        mock_app = MagicMock()
        mock_cmd_line = MagicMock()
        mock_app.query_one.return_value = mock_cmd_line

        show_command_error(mock_app, None)

        mock_cmd_line.show_persistent_message.assert_called_once_with(
            "Unknown error"
        )


class TestCommandCallbackUnknownCommand:
    """Tests for callback behavior with unknown commands."""

    @pytest.mark.asyncio
    async def test_unknown_command_hides_prompt(self) -> None:
        """Unknown command hides prompt before showing error."""
        mock_ctx = MagicMock()
        mock_app = MagicMock()
        mock_prompt = MagicMock()
        mock_cmd_line = MagicMock()

        def query_one_side_effect(query, widget_type=None):
            if widget_type is None:
                from platyplaty.ui.command_prompt import CommandPrompt
                if query == CommandPrompt:
                    return mock_prompt
            if query == "#command_line":
                return mock_cmd_line
            return MagicMock()

        mock_app.query_one.side_effect = query_one_side_effect

        callback = create_command_callback(mock_ctx, mock_app)
        await callback("unknowncmd")

        mock_prompt.hide.assert_called_once()

    @pytest.mark.asyncio
    async def test_unknown_command_shows_persistent_message(self) -> None:
        """Unknown command shows persistent message with correct format."""
        mock_ctx = MagicMock()
        mock_app = MagicMock()
        mock_prompt = MagicMock()
        mock_cmd_line = MagicMock()

        def query_one_side_effect(query, widget_type=None):
            if widget_type is None:
                from platyplaty.ui.command_prompt import CommandPrompt
                if query == CommandPrompt:
                    return mock_prompt
            if query == "#command_line":
                return mock_cmd_line
            return MagicMock()

        mock_app.query_one.side_effect = query_one_side_effect

        callback = create_command_callback(mock_ctx, mock_app)
        await callback("badcmd")

        mock_cmd_line.show_persistent_message.assert_called_once()
        call_args = mock_cmd_line.show_persistent_message.call_args[0][0]
        assert "Command not found: 'badcmd'" in call_args
