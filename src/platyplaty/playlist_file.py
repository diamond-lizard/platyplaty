#!/usr/bin/env python3
"""Playlist file I/O for Platyplaty.

Handles reading and writing .platy playlist files.
"""

from pathlib import Path

from platyplaty.playlist_validation import (
    InvalidExtensionError,
    expand_path,
    is_absolute_path,
    raise_if_errors,
)


def parse_playlist_file(filepath: Path) -> list[Path]:
    """Parse a .platy playlist file and return list of preset paths.

    Args:
        filepath: Path to the .platy file.

    Returns:
        List of absolute Path objects for each preset.

    Raises:
        RelativePathError: If any path is relative.
        InvalidExtensionError: If any path doesn't end with .milk.
        FileNotFoundError: If the file doesn't exist.
        PermissionError: If the file can't be read.
    """
    content = filepath.read_text()
    return parse_playlist_content(content)


def parse_playlist_content(content: str) -> list[Path]:
    """Parse playlist content and return list of preset paths.

    Args:
        content: The text content of a playlist file.

    Returns:
        List of absolute Path objects for each preset.

    Raises:
        RelativePathError: If any path is relative.
        InvalidExtensionError: If any path doesn't end with .milk.
    """
    lines = content.splitlines()
    relative_errors: list[int] = []
    extension_errors: list[int] = []
    paths: list[Path] = []

    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            continue
        if not is_absolute_path(stripped):
            relative_errors.append(line_num)
            continue
        if not stripped.lower().endswith('.milk'):
            extension_errors.append(line_num)
            continue
        paths.append(expand_path(stripped))

    raise_if_errors(relative_errors, extension_errors)
    return paths


def write_playlist_file(filepath: Path, presets: list[Path]) -> None:
    """Write a list of preset paths to a .platy playlist file.

    Args:
        filepath: Path where the playlist will be saved.
        presets: List of preset paths to write.

    Raises:
        InvalidExtensionError: If filepath doesn't end with .platy.
        PermissionError: If the file can't be written.
        OSError: If write fails for other reasons.
    """
    if not filepath.suffix.lower() == '.platy':
        raise InvalidExtensionError("filename must end with .platy")
    content = "\n".join(str(p) for p in presets)
    if content:
        content += "\n"
    filepath.write_text(content)
