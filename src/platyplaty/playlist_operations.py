#!/usr/bin/env python3
"""Playlist modification operations.

Functions for adding, removing, and reordering presets.
"""

from pathlib import Path
import random


def add_preset(presets: list[Path], path: Path) -> None:
    """Add a preset at the end of the playlist.

    Args:
        presets: List of preset paths (modified in place).
        path: Path of the preset to add.
    """
    presets.append(path)


def remove_preset(presets: list[Path], index: int) -> None:
    """Remove the preset at the given index.

    Args:
        presets: List of preset paths (modified in place).
        index: Index of the preset to remove.
    """
    del presets[index]


def move_preset_up(presets: list[Path], index: int) -> bool:
    """Move preset at index up by one position.

    Args:
        presets: List of preset paths (modified in place).
        index: Index of the preset to move up.

    Returns:
        True if moved, False if already at top.
    """
    if index <= 0:
        return False
    presets[index - 1], presets[index] = presets[index], presets[index - 1]
    return True


def move_preset_down(presets: list[Path], index: int) -> bool:
    """Move preset at index down by one position.

    Args:
        presets: List of preset paths (modified in place).
        index: Index of the preset to move down.

    Returns:
        True if moved, False if already at bottom.
    """
    if index >= len(presets) - 1:
        return False
    presets[index], presets[index + 1] = presets[index + 1], presets[index]
    return True

def shuffle_presets(presets: list[Path]) -> None:
    """Shuffle the playlist in place.

    Args:
        presets: List of preset paths (modified in place).
    """
    random.shuffle(presets)
