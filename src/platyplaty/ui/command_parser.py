#!/usr/bin/env python3
"""Command parser for the command prompt.

This module parses and validates commands entered at the command prompt.
Supported commands: load, save, clear, shuffle.
"""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ParsedCommand:
    """Result of parsing a command."""

    name: str
    argument: str | None = None


class CommandParseError(Exception):
    """Error raised when command parsing fails."""


def parse_command(input_text: str) -> ParsedCommand:
    """Parse a command string into name and argument.

    Args:
        input_text: The raw command input (e.g., "load /path/to/file").

    Returns:
        ParsedCommand with name and optional argument.

    Raises:
        CommandParseError: If the command is unknown or invalid.
    """
    parts = input_text.strip().split(" ", 1)
    if not parts or not parts[0]:
        raise CommandParseError("Empty command")
    name = parts[0]
    argument = parts[1] if len(parts) > 1 else None
    valid_commands = {"load", "save", "clear", "shuffle"}
    if name not in valid_commands:
        raise CommandParseError(f"Command not found: '{name}'")
    return ParsedCommand(name=name, argument=argument)


def expand_path(path: str, base_dir: Path) -> Path:
    """Expand tilde and environment variables in a path.

    Args:
        path: The path string to expand.
        base_dir: Base directory for resolving relative paths.

    Returns:
        Expanded and resolved Path.
    """
    expanded = os.path.expandvars(os.path.expanduser(path))
    result = Path(expanded)
    if not result.is_absolute():
        result = base_dir / result
    return result
