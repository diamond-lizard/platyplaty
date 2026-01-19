#!/usr/bin/env python3
"""Preset validation functions for checking file accessibility."""

from pathlib import Path


def is_broken_symlink(path: Path) -> bool:
    """Check if path is a broken symlink.

    Args:
        path: The path to check.

    Returns:
        True if path is a symlink whose target does not exist.
    """
    return path.is_symlink() and not path.exists()


def is_readable(path: Path) -> bool:
    """Check if a file is readable.

    Args:
        path: The path to check.

    Returns:
        True if the file exists and is readable.
    """
    try:
        with path.open("rb"):
            return True
    except OSError:
        return False


def is_valid_preset(path: Path) -> bool:
    """Check if a preset is valid (exists, readable, not broken symlink).

    A preset is considered valid if:
    - The file exists
    - The file is readable
    - It is not a broken symlink

    Args:
        path: The path to the preset file.

    Returns:
        True if the preset is valid and playable.
    """
    if is_broken_symlink(path):
        return False
    if not path.exists():
        return False
    return is_readable(path)
