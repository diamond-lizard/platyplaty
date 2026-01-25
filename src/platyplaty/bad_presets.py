#!/usr/bin/env python3
"""Bad preset registry for crash tracking.

This module maintains a session-scoped set of preset paths that have caused
the renderer to crash. When a preset crashes the renderer, its resolved path
is added to this registry. The registry is used by autoplay to skip bad
presets automatically.

The registry is session-only: it clears when platyplaty restarts, allowing
users to retry presets that may work after libprojectM updates.
"""
from pathlib import Path

_bad_presets: set[Path] = set()


def mark_preset_as_bad(path: Path) -> None:
    """Mark a preset as bad (crashed the renderer).

    Args:
        path: The path to the preset file. Will be resolved to handle
            symlinks pointing to the same target file.
    """
    _bad_presets.add(path.resolve())


def is_preset_bad(path: Path) -> bool:
    """Check if a preset is marked as bad.

    Args:
        path: The path to the preset file. Will be resolved to handle
            symlinks pointing to the same target file.

    Returns:
        True if the preset has previously crashed the renderer, False otherwise.
    """
    return path.resolve() in _bad_presets
