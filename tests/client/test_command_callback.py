#!/usr/bin/env python3
"""Unit tests for command callback behavior.

Tests that command execution failures correctly hide the prompt and show
persistent messages.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.command_prompt_handler import create_command_callback


def make_query_side_effect(mock_prompt, mock_cmd_line):
    """Create a query_one side effect for testing command callbacks."""
    def side_effect(query, widget_type=None):
        from platyplaty.ui.command_prompt import CommandPrompt
        if widget_type is None and query == CommandPrompt:
            return mock_prompt
        if query == "#command_line":
            return mock_cmd_line
        return MagicMock()
    return side_effect


class TestCommandCallbackUnknownCommand:
    """Tests for callback behavior with unknown commands."""

    @pytest.mark.asyncio
    async def test_unknown_command_hides_prompt(self) -> None:
        """Unknown command hides prompt before showing error."""
        mock_ctx = MagicMock()
        mock_app = MagicMock()
        mock_prompt = MagicMock()
        mock_cmd_line = MagicMock()

        mock_app.query_one.side_effect = make_query_side_effect(
            mock_prompt, mock_cmd_line
        )

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

        mock_app.query_one.side_effect = make_query_side_effect(
            mock_prompt, mock_cmd_line
        )

        callback = create_command_callback(mock_ctx, mock_app)
        await callback("badcmd")

        mock_cmd_line.show_persistent_message.assert_called_once()
        call_args = mock_cmd_line.show_persistent_message.call_args[0][0]
        assert "Command not found: 'badcmd'" in call_args
