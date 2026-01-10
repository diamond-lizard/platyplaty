#!/usr/bin/env python3
"""Path display functions for file browser.

This module provides functions to split paths into components with
type information for coloring in the path display line.
"""

from pathlib import Path
import stat
from rich.text import Text

from platyplaty.ui.path_types import PathComponent, PathComponentType
from platyplaty.ui.colors import (
    BROKEN_SYMLINK_COLOR,
    DIRECTORY_COLOR,
    SELECTED_COLOR,
    SYMLINK_COLOR,
)


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


def _get_component_color(component: PathComponent) -> str:
    """Get the display color for a path component.

    Args:
        component: The path component to get a color for.

    Returns:
        Color string for Rich styling.
    """
    if component.is_selected:
        return SELECTED_COLOR
    if component.component_type == PathComponentType.SYMLINK:
        return SYMLINK_COLOR
    if component.component_type == PathComponentType.BROKEN_SYMLINK:
        return BROKEN_SYMLINK_COLOR
    return DIRECTORY_COLOR


def render_path_components(components: list[PathComponent]) -> Text:
    """Render a list of path components to a styled Rich Text.

    Each component is colored according to its type:
    - Directory: blue
    - Symlink: cyan
    - Broken symlink: magenta
    - Selected (final): bright white

    Slashes between components match the preceding component's color.

    Args:
        components: List of PathComponent objects to render.

    Returns:
        Rich Text object with styled path.
    """
    result = Text()
    for i, comp in enumerate(components):
        color = _get_component_color(comp)
        if i == 0 and comp.name == "/":
            result.append("/", style=color)
        else:
            if i > 0 and components[i - 1].name != "/":
                prev_color = _get_component_color(components[i - 1])
                result.append("/", style=prev_color)
            result.append(comp.name, style=color)
    return result
