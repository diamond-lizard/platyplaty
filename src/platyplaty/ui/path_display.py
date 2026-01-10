#!/usr/bin/env python3
"""Path display functions for file browser.

This module provides functions to split paths into components with
type information for coloring in the path display line.
"""

from pathlib import Path
import stat

from platyplaty.ui.path_types import PathComponent, PathComponentType


def _get_symlink_type(path: Path) -> PathComponentType:
    """Determine the type of a symlink (valid or broken).

    Args:
        path: Path to a symlink.

    Returns:
        PathComponentType.SYMLINK if target exists, BROKEN_SYMLINK otherwise.
    """
    try:
        path.stat()
        return PathComponentType.SYMLINK
    except OSError:
        return PathComponentType.BROKEN_SYMLINK


def _get_component_type(path: Path) -> PathComponentType:
    """Determine the type of a path component using lstat.

    Uses lstat to detect symlinks without following them.

    Args:
        path: The full path to check (not just the component name).

    Returns:
        PathComponentType indicating whether the component is a directory,
        symlink, broken symlink, or file.
    """
    try:
        st = path.lstat()
    except OSError:
        return PathComponentType.BROKEN_SYMLINK
    if stat.S_ISLNK(st.st_mode):
        return _get_symlink_type(path)
    if stat.S_ISDIR(st.st_mode):
        return PathComponentType.DIRECTORY
    return PathComponentType.FILE


def split_path_to_components(
    path: Path | str, mark_selected: bool = True
) -> list[PathComponent]:
    """Split a path into a list of PathComponents with type information.

    Each component in the path is examined to determine its type (directory,
    symlink, broken symlink, or file). Uses lstat to detect symlinks without
    following them, preserving the logical path.

    Args:
        path: The path to split (as Path or str).
        mark_selected: If True, mark the final component as selected.
            Set to False for inaccessible directories (per REQ-0700).

    Returns:
        List of PathComponent objects representing each path component.
    """
    path = Path(path) if isinstance(path, str) else path
    parts = path.parts
    components: list[PathComponent] = []
    for i, part in enumerate(parts):
        current_path = Path(*parts[: i + 1])
        is_last = i == len(parts) - 1
        comp_type = _get_component_type(current_path)
        is_selected = is_last and mark_selected
        components.append(PathComponent(part, comp_type, is_selected))
    return components
