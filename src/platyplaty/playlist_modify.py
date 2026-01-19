#!/usr/bin/env python3
"""Functions for modifying playlists with dirty flag and broken index tracking."""

from pathlib import Path

from platyplaty import playlist_broken as broken
from platyplaty import playlist_operations as ops


def add_preset_to_playlist(
    presets: list[Path], broken_indices: set[int], path: Path
) -> None:
    """Add a preset at the end of the playlist and validate it.

    Args:
        presets: List of preset paths (modified in place).
        broken_indices: Set of broken indices (modified in place).
        path: Path of the preset to add.
    """
    ops.add_preset(presets, path)
    broken.validate_new_preset(broken_indices, path, len(presets) - 1)


def remove_preset_from_playlist(
    presets: list[Path], broken_indices: set[int], index: int
) -> set[int]:
    """Remove a preset and adjust broken indices.

    Args:
        presets: List of preset paths (modified in place).
        broken_indices: Set of broken indices.
        index: Index of the preset to remove.

    Returns:
        Updated set of broken indices.
    """
    ops.remove_preset(presets, index)
    return broken.adjust_broken_indices_after_remove(broken_indices, index)


def move_preset_up_in_playlist(
    presets: list[Path], broken_indices: set[int], index: int
) -> bool:
    """Move a preset up and update broken indices if needed.

    Args:
        presets: List of preset paths (modified in place).
        broken_indices: Set of broken indices (modified in place).
        index: Index of the preset to move.

    Returns:
        True if moved, False if already at top.
    """
    result = ops.move_preset_up(presets, index)
    if result:
        broken.swap_broken_indices(broken_indices, index - 1, index)
    return result


def move_preset_down_in_playlist(
    presets: list[Path], broken_indices: set[int], index: int
) -> bool:
    """Move a preset down and update broken indices if needed.

    Args:
        presets: List of preset paths (modified in place).
        broken_indices: Set of broken indices (modified in place).
        index: Index of the preset to move.

    Returns:
        True if moved, False if already at bottom.
    """
    result = ops.move_preset_down(presets, index)
    if result:
        broken.swap_broken_indices(broken_indices, index, index + 1)
    return result
