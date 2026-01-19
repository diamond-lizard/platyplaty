#!/usr/bin/env python3
"""Tests for command_parser module."""

import pytest

from platyplaty.ui.command_parser import (
    CommandParseError,
    ParsedCommand,
    parse_command,
)


class TestParseCommand:
    """Tests for parse_command function."""

    def test_load_with_path(self) -> None:
        """Load command with path argument."""
        result = parse_command("load /path/to/file.platy")
        assert result == ParsedCommand(name="load", argument="/path/to/file.platy")

    def test_save_with_path(self) -> None:
        """Save command with path argument."""
        result = parse_command("save /path/to/file.platy")
        assert result == ParsedCommand(name="save", argument="/path/to/file.platy")

    def test_save_without_path(self) -> None:
        """Save command without argument."""
        result = parse_command("save")
        assert result == ParsedCommand(name="save", argument=None)

    def test_clear_command(self) -> None:
        """Clear command has no argument."""
        result = parse_command("clear")
        assert result == ParsedCommand(name="clear", argument=None)

    def test_shuffle_command(self) -> None:
        """Shuffle command has no argument."""
        result = parse_command("shuffle")
        assert result == ParsedCommand(name="shuffle", argument=None)

    def test_unknown_command_raises_error(self) -> None:
        """Unknown command raises CommandParseError."""
        with pytest.raises(CommandParseError) as exc_info:
            parse_command("unknown")
        assert "Command not found: 'unknown'" in str(exc_info.value)

    def test_empty_command_raises_error(self) -> None:
        """Empty command raises CommandParseError."""
        with pytest.raises(CommandParseError) as exc_info:
            parse_command("")
        assert "Empty command" in str(exc_info.value)

    def test_whitespace_only_raises_error(self) -> None:
        """Whitespace-only command raises CommandParseError."""
        with pytest.raises(CommandParseError) as exc_info:
            parse_command("   ")
        assert "Empty command" in str(exc_info.value)

    def test_command_with_leading_whitespace(self) -> None:
        """Commands with leading whitespace are handled."""
        result = parse_command("  load /path/file.platy")
        assert result == ParsedCommand(name="load", argument="/path/file.platy")

    def test_command_case_sensitive(self) -> None:
        """Commands are case-sensitive (must be lowercase)."""
        with pytest.raises(CommandParseError) as exc_info:
            parse_command("LOAD /path/file.platy")
        assert "Command not found: 'LOAD'" in str(exc_info.value)

    def test_path_with_spaces(self) -> None:
        """Path argument can contain spaces."""
        result = parse_command("load /path/to/my file.platy")
        assert result == ParsedCommand(
            name="load", argument="/path/to/my file.platy"
        )
