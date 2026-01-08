#!/usr/bin/env python3
"""Preset directory expansion and validation.

This module provides functions for expanding environment variables
in preset directory paths and validating that directories exist.
"""

from pathlib import Path

from platyplaty.errors import StartupError
from platyplaty.paths import UndefinedEnvVarError, expand_path, resolve_path


def expand_preset_dirs(preset_dirs: list[str]) -> list[str]:
    """Expand and resolve preset directory paths.

    Args:
        preset_dirs: List of directory paths from config.

    Returns:
        List of absolute paths.

    Raises:
        StartupError: If an environment variable is undefined.
    """
    result: list[str] = []
    for path in preset_dirs:
        try:
            expanded = expand_path(path)
        except UndefinedEnvVarError as e:
            raise StartupError(str(e)) from None
        result.append(resolve_path(expanded))
    return result


def validate_preset_dirs(preset_dirs: list[str]) -> None:
    """Validate that all preset directories exist.

    Args:
        preset_dirs: List of absolute directory paths.

    Raises:
        StartupError: If any directory does not exist.
    """
    for path in preset_dirs:
        if not Path(path).is_dir():
            raise StartupError(f"Preset directory not found: {path}")
