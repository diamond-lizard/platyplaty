#!/usr/bin/env python3
"""Helper functions for autoplay preset validation and loading."""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.playlist import Playlist


def is_preset_playable(path: Path) -> bool:
    """Check if a preset file is playable.

    Args:
        path: Path to the preset file.

    Returns:
        True if the file exists, is readable, is not a broken symlink,
        and has not been marked as bad (crashed the renderer).
    """
    from platyplaty.bad_presets import is_preset_bad
    from platyplaty.preset_validator import is_valid_preset
    if is_preset_bad(path):
        return False
    return is_valid_preset(path)



def validate_and_mark_broken(playlist: "Playlist", index: int) -> bool:
    """Re-validate preset at index and update broken_indices if needed.

    Args:
        playlist: The playlist containing the preset.
        index: Index of the preset to validate.

    Returns:
        True if preset is valid, False if broken.
    """
    if index < 0 or index >= len(playlist.presets):
        return False
    path = playlist.presets[index]
    if is_preset_playable(path):
        return True
    playlist.broken_indices.add(index)
    return False


def find_next_playable(playlist: "Playlist", start_index: int) -> int | None:
    """Find the next playable preset starting from start_index.

    Iterates through the playlist starting from start_index + 1,
    wrapping to the beginning and stopping before reaching start_index again.
    Marks any broken presets in playlist.broken_indices.

    Args:
        playlist: The playlist to search.
        start_index: Index to start searching from (not included).

    Returns:
        Index of the next playable preset, or None if no playable preset found.
    """
    presets = playlist.presets
    if not presets:
        return None
    count = len(presets)
    for offset in range(1, count + 1):
        index = (start_index + offset) % count
        if validate_and_mark_broken(playlist, index):
            return index
    return None
