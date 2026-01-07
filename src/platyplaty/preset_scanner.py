#!/usr/bin/env python3
"""Preset scanner module for Platyplaty.

Handles preset directory scanning and shuffling.
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
