#!/usr/bin/env python3
"""Validation helpers for playlist file parsing.

Contains path validation and error handling for playlist files.
"""

from pathlib import Path


class PlaylistFileError(Exception):
    """Base exception for playlist file errors."""


class RelativePathError(PlaylistFileError):
    """Raised when a playlist contains a relative path."""


class InvalidExtensionError(PlaylistFileError):
    """Raised when paths don't end with .milk or .platy."""


def expand_path(path_str: str) -> Path:
    """Expand ~ and ~username in a path string.

    Args:
        path_str: A path string that may contain ~ or ~username.

    Returns:
        Expanded Path object.
    """
    return Path(path_str).expanduser()


def is_absolute_path(path_str: str) -> bool:
    """Check if a path string represents an absolute path.

    Args:
        path_str: A path string to check.

    Returns:
        True if path starts with / or ~, False otherwise.
    """
    return path_str.startswith('/') or path_str.startswith('~')


def raise_if_errors(relative: list[int], extension: list[int]) -> None:
    """Raise appropriate exception if validation errors exist.

    Args:
        relative: List of line numbers with relative paths.
        extension: List of line numbers with non-.milk extensions.

    Raises:
        RelativePathError: If any relative paths were found.
        InvalidExtensionError: If any non-.milk paths were found.
    """
    if relative:
        raise RelativePathError(f"line {relative[0]}")
    if extension:
        lines = ", ".join(str(n) for n in extension)
        raise InvalidExtensionError(f"lines {lines}")
