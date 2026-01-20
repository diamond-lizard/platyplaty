#!/usr/bin/env python3
"""Validation functions for the load playlist command."""

from pathlib import Path


def validate_playlist_path(filepath: Path) -> str | None:
    """Validate the playlist file path.

    Args:
        filepath: Path to the playlist file.

    Returns:
        Error message if invalid, None if valid.
    """
    if not filepath.exists():
        return f"Error: could not load playlist: file not found: {filepath}"
    if not filepath.is_file():
        return f"Error: could not load playlist: not a file: {filepath}"
    return None
