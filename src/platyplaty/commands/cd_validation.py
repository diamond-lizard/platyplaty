#!/usr/bin/env python3
"""Path validation utilities for the cd command.

Provides functions for validating that a path exists, is a directory,
and is accessible.
"""

import os
from pathlib import Path


def validate_cd_path(path: Path) -> str | None:
    """Validate that a path is a valid directory for cd.

    Checks the path for existence, type (directory vs file), accessibility,
    and symlink status. Returns the first applicable error or None if valid.

    Args:
        path: The path to validate.

    Returns:
        Error message string if invalid, or None if the path is a valid directory.
    """
    # Check for broken symlink first (is_symlink but not exists)
    if path.is_symlink() and not path.exists():
        return f"Error: cd: broken symlink: '{path}'"
    # Check existence
    if not path.exists():
        return f"Error: cd: no such directory: '{path}'"
    # Check if symlink points to non-directory
    if path.is_symlink() and not path.is_dir():
        return f"Error: cd: not a directory: '{path}'"
    # Check if regular file (not a directory)
    if path.is_file():
        return f"Error: cd: not a directory: '{path}'"
    # Check for permission to list directory contents
    try:
        os.listdir(path)
    except PermissionError:
        return f"Error: cd: permission denied: '{path}'"
    return None
