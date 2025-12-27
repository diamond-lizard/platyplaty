#!/usr/bin/env python3
"""Playlist module for Platyplaty.

Handles preset directory scanning, playlist building, and navigation.
"""

import random
from pathlib import Path


class NoPresetsFoundError(Exception):
    """Raised when no .milk files are found in preset directories."""
def _is_milk_file(path: Path) -> bool:
    """Check if a path is a .milk file (case-insensitive)."""
    return path.is_file() and path.suffix.lower() == ".milk"

def scan_preset_dirs(dirs: list[str]) -> list[Path]:
    """Scan directories for .milk preset files.

    Performs a flat (non-recursive) scan of each directory.

    Args:
        dirs: List of directory paths to scan.

    Returns:
        List of Path objects for all .milk files found.

    Raises:
        NoPresetsFoundError: If no .milk files are found.
    """
    all_files = [
        p.resolve() for d in dirs for p in Path(d).iterdir() if _is_milk_file(p)
    ]
    # Deduplicate by absolute path
    seen: set[Path] = set()
    result: list[Path] = []
    for p in all_files:
        if p not in seen:
            seen.add(p)
            result.append(p)
    if not result:
        dirs_list = ", ".join(dirs)
        raise NoPresetsFoundError(f"No .milk files found in: {dirs_list}")
    return sorted(result, key=lambda p: str(p).lower())


def shuffle_presets(presets: list[Path]) -> list[Path]:
    """Shuffle the preset list in place and return it.

    Args:
        presets: List of preset paths to shuffle.

    Returns:
        The same list, shuffled in place.
    """
    random.shuffle(presets)
    return presets


class Playlist:
    """Manages a list of presets with navigation.

    Attributes:
        presets: List of preset paths.
        loop: Whether to wrap around at the end.
    """

    presets: list[Path]
    loop: bool
    _index: int

    def __init__(self, presets: list[Path], loop: bool = True) -> None:
        """Initialize the playlist.

        Args:
            presets: List of preset paths.
            loop: Whether to wrap around when reaching the end.
        """
        self.presets = presets
        self.loop = loop
        self._index = 0

    def current(self) -> Path:
        """Return the current preset path."""
        return self.presets[self._index]

    def at_end(self) -> bool:
        """Return True if at the last preset."""
        return self._index >= len(self.presets) - 1

    def next(self) -> Path | None:
        """Advance to the next preset.

        Returns:
            The next preset path, or None if at end and loop is False.
        """
        if self.at_end():
            if self.loop:
                self._index = 0
            else:
                return None
        else:
            self._index += 1
        return self.presets[self._index]

    def previous(self) -> Path | None:
        """Move to the previous preset.

        Returns:
            The previous preset path, or None if at start and loop is False.
        """
        if self._index == 0:
            if self.loop:
                self._index = len(self.presets) - 1
            else:
                return None
        else:
            self._index -= 1
        return self.presets[self._index]
