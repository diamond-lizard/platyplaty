#!/usr/bin/env python3
"""Path argument resolution for Platyplaty startup.

This module handles resolving the optional path argument to determine
the start directory and playlist path.
"""

from dataclasses import dataclass
from pathlib import Path

from platyplaty.errors import StartupError


@dataclass
class ResolvedPath:
    """Result of resolving the path argument."""

    start_directory: Path
    playlist_path: Path | None


def resolve_path_argument(path_argument: str | None) -> ResolvedPath:
    """Resolve the path argument to start directory and playlist path.

    Args:
        path_argument: Optional path to directory or .platy file.

    Returns:
        ResolvedPath with start_directory and playlist_path.

    Raises:
        StartupError: If path does not exist or is invalid type.
    """
    if path_argument is None:
        return ResolvedPath(start_directory=Path.cwd(), playlist_path=None)

    path = Path(path_argument)
    if not path.exists():
        raise StartupError(f"Path does not exist: {path_argument}")

    if path.is_dir():
        return ResolvedPath(start_directory=path, playlist_path=None)

    if path.is_file():
        if path.suffix.lower() == ".platy":
            return ResolvedPath(start_directory=path.parent, playlist_path=path)
        raise StartupError(f"File must have .platy extension: {path_argument}")

    raise StartupError(f"Path is not a file or directory: {path_argument}")
