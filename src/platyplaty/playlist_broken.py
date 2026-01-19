#!/usr/bin/env python3
"""Helper functions for managing broken preset indices in playlists."""

from pathlib import Path


def validate_new_preset(broken_indices: set[int], path: Path, new_index: int) -> None:
    """Check if newly added preset is broken and update broken_indices.

    Args:
        broken_indices: Set of broken preset indices to update.
        path: Path to the preset file.
        new_index: Index where the preset was added.
    """
    from platyplaty.preset_validator import is_valid_preset

    if not is_valid_preset(path):
        broken_indices.add(new_index)


def adjust_broken_indices_after_remove(
    broken_indices: set[int], removed_index: int
) -> set[int]:
    """Adjust broken_indices after a preset is removed.

    Args:
        broken_indices: Set of broken preset indices to update.
        removed_index: Index of the removed preset.

    Returns:
        Updated set of broken indices with positions adjusted.
    """
    broken_indices.discard(removed_index)
    return {i - 1 if i > removed_index else i for i in broken_indices}


def swap_broken_indices(broken_indices: set[int], idx1: int, idx2: int) -> None:
    """Swap positions in broken_indices when presets are swapped.

    Args:
        broken_indices: Set of broken preset indices to update.
        idx1: First index being swapped.
        idx2: Second index being swapped.
    """
    has_idx1 = idx1 in broken_indices
    has_idx2 = idx2 in broken_indices
    if has_idx1 == has_idx2:
        return  # No change needed - both broken or both valid
    if has_idx1:
        broken_indices.discard(idx1)
        broken_indices.add(idx2)
        return
    broken_indices.discard(idx2)
    broken_indices.add(idx1)
