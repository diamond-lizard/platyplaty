"""Playlist preview creation for the file browser widget.

This module provides functions for parsing .platy files for right pane
preview, using tolerant parsing that silently skips invalid lines.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from platyplaty.playlist_validation import expand_path, is_absolute_path
from platyplaty.ui.file_browser_types import (
    RightPaneBinaryFile,
    RightPaneContent,
    RightPaneNoMilk,
    RightPanePlaylistPreview,
)
from platyplaty.ui.playlist_display_name import compute_display_names

if TYPE_CHECKING:
    from platyplaty.ui.directory_types import DirectoryEntry
    from platyplaty.ui.file_browser import FileBrowser


def _parse_playlist_tolerant(content: str) -> list[Path]:
    """Parse playlist content, silently skipping invalid lines.

    Args:
        content: The raw content of a .platy file.

    Returns:
        List of expanded Path objects for valid lines only.
    """
    result: list[Path] = []
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if not is_absolute_path(stripped):
            continue
        if not stripped.lower().endswith('.milk'):
            continue
        try:
            expanded = expand_path(stripped)
        except RuntimeError:
            continue
        result.append(expanded)
    return result


def make_playlist_preview(
    browser: FileBrowser, entry: DirectoryEntry
) -> RightPaneContent:
    """Create playlist preview content for a .platy file.

    Args:
        browser: The file browser instance.
        entry: The directory entry to preview.

    Returns:
        RightPanePlaylistPreview with disambiguated names,
        RightPaneNoMilk if empty/no valid entries,
        RightPaneBinaryFile if decode fails,
        or None if permission denied or file not found.
    """
    file_path = browser.current_dir / entry.name
    try:
        raw_bytes = file_path.read_bytes()
    except (PermissionError, FileNotFoundError):
        return None
    try:
        content = raw_bytes.decode('utf-8')
    except UnicodeDecodeError:
        return RightPaneBinaryFile()
    paths = _parse_playlist_tolerant(content)
    if not paths:
        return RightPaneNoMilk()
    names = compute_display_names(paths)
    return RightPanePlaylistPreview(tuple(names))
