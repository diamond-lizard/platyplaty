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


