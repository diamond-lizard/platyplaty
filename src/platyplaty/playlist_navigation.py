#!/usr/bin/env python3
"""Playlist navigation functions.

Pure functions for navigating through a list of presets.
"""

from pathlib import Path


def get_current(presets: list[Path], playing_index: int | None) -> Path:
    """Return the preset at the current playing index.

    Args:
        presets: List of preset paths.
        playing_index: Current playing index, or None if idle.

    Returns:
        The preset path at the playing index.

    Raises:
        ValueError: If playing_index is None (idle state).
    """
    if playing_index is None:
        raise ValueError("No preset is currently playing")
    return presets[playing_index]


def is_at_end(presets: list[Path], playing_index: int | None) -> bool:
    """Check if at the last preset.

    Args:
        presets: List of preset paths.
        playing_index: Current playing index, or None if idle.

    Returns:
        True if at the last preset or idle.
    """
    if playing_index is None:
        return True
    return playing_index >= len(presets) - 1


def advance_next(
    presets: list[Path], playing_index: int | None, loop: bool
) -> tuple[int, Path] | None:
    """Advance to the next preset.

    Args:
        presets: List of preset paths.
        playing_index: Current playing index, or None if idle.
        loop: Whether to wrap around at the end.

    Returns:
        Tuple of (new_index, preset) or None if at end and not looping.
    """
    if not presets:
        return None
    if playing_index is None:
        return None
    at_end = playing_index >= len(presets) - 1
    if at_end and not loop:
        return None
    new_index = 0 if at_end else playing_index + 1
    return (new_index, presets[new_index])


def go_previous(
    presets: list[Path], playing_index: int | None, loop: bool
) -> tuple[int, Path] | None:
    """Move to the previous preset.

    Args:
        presets: List of preset paths.
        playing_index: Current playing index, or None if idle.
        loop: Whether to wrap around at the start.

    Returns:
        Tuple of (new_index, preset) or None if at start and not looping.
    """
    if not presets:
        return None
    if playing_index is None:
        return None
    at_start = playing_index == 0
    if at_start and not loop:
        return None
    new_index = len(presets) - 1 if at_start else playing_index - 1
    return (new_index, presets[new_index])
