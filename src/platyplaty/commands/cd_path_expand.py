#!/usr/bin/env python3
"""Path expansion utilities for the cd command.

Provides functions for detecting undefined and empty environment variables,
and for expanding paths with tilde and environment variable support.
"""

import os
import re
from pathlib import Path

# Pattern matches $VAR or ${VAR} and captures the variable name
_ENV_VAR_PATTERN = re.compile(
    r'\$(?:([A-Za-z_][A-Za-z0-9_]*)|\{([A-Za-z_][A-Za-z0-9_]*)\})'
)


def find_undefined_variables(path_str: str) -> list[str]:
    """Find environment variable references that are not defined.

    Scans the input string for $VARNAME or ${VARNAME} patterns and returns
    a list of variable names that are not defined in os.environ.

    Args:
        path_str: The path string to scan.

    Returns:
        List of undefined variable names (without the $ prefix).
    """
    undefined = []
    for match in _ENV_VAR_PATTERN.finditer(path_str):
        var_name = match.group(1) or match.group(2)
        if var_name not in os.environ:
            undefined.append(var_name)
    return undefined


def find_empty_variables(path_str: str) -> list[str]:
    """Find environment variable references that are defined but empty.

    Scans the input string for $VARNAME or ${VARNAME} patterns and returns
    a list of variable names that ARE defined in os.environ but have empty
    string values.

    Args:
        path_str: The path string to scan.

    Returns:
        List of variable names that are defined but empty.
    """
    empty = []
    for match in _ENV_VAR_PATTERN.finditer(path_str):
        var_name = match.group(1) or match.group(2)
        if var_name in os.environ and os.environ[var_name] == "":
            empty.append(var_name)
    return empty


def _format_variable_error(prefix: str, var_names: list[str]) -> str:
    """Format an error message for undefined or empty variables."""
    quoted = [f"'${v}'" for v in var_names]
    if len(var_names) == 1:
        return f"{prefix}: {quoted[0]}"
    return f"{prefix}s: {', '.join(quoted)}"


def expand_cd_path(path_str: str, base_dir: Path) -> tuple[Path | None, str | None]:
    """Expand a cd command path argument to a normalized absolute Path.

    Handles tilde expansion, environment variables, relative paths, and
    normalization. Reports errors for undefined or empty variables.

    Args:
        path_str: The path string from the cd command argument.
        base_dir: Base directory for resolving relative paths.

    Returns:
        Tuple of (expanded_path, None) on success, or (None, error_message) on failure.
    """
    undefined = find_undefined_variables(path_str)
    if undefined:
        err = _format_variable_error("Error: cd: undefined variable", undefined)
        return (None, err)
    empty = find_empty_variables(path_str)
    if empty:
        return (None, _format_variable_error("Error: cd: empty variable", empty))
    path_str = path_str.strip()
    if path_str == "" or path_str == "~":
        return (Path.home(), None)
    expanded = os.path.expandvars(path_str)
    expanded = os.path.expanduser(expanded)
    if expanded.startswith("~"):
        username = expanded[1:].split("/")[0]
        return (None, f"Error: cd: no such user: '{username}'")
    result = Path(expanded)
    if not result.is_absolute():
        result = base_dir / result
    result = Path(os.path.normpath(str(result)))
    return (result, None)
