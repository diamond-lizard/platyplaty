#!/usr/bin/env python3
"""Path expansion and resolution utilities for Platyplaty."""

import os
import re
from pathlib import Path


class UndefinedEnvVarError(Exception):
    """Raised when an environment variable in a path is undefined."""


def expand_path(path: str) -> str:
    """Expand tilde and environment variables in a path.

    Args:
        path: Path that may contain ~ or $VAR references.

    Returns:
        Expanded path string.

    Raises:
        UndefinedEnvVarError: If a referenced env var is not defined.
    """
    # Check for undefined environment variables before expansion
    for match in re.finditer(r'\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?', path):
        var_name = match.group(1)
        if var_name not in os.environ:
            msg = f"Environment variable ${var_name} is not defined (in path '{path}')"
            raise UndefinedEnvVarError(msg)
    expanded = os.path.expanduser(path)
    expanded = os.path.expandvars(expanded)
    return expanded


def resolve_path(path: str) -> str:
    """Resolve a path to an absolute path.

    Relative paths are resolved from the current working directory.

    Args:
        path: Path to resolve (may be relative or absolute).

    Returns:
        Absolute path string.
    """
    return str(Path(path).resolve())
