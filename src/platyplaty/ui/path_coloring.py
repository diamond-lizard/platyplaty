#!/usr/bin/env python3
"""Path coloring functions for file browser path display.

This module provides functions to color path components and render
styled path strings for the path display line.
"""

from rich.text import Text

from platyplaty.ui.colors import (
    BROKEN_SYMLINK_COLOR,
    DIRECTORY_COLOR,
    SELECTED_COLOR,
    SYMLINK_COLOR,
)
from platyplaty.ui.path_types import PathComponent, PathComponentType


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


def _needs_separator(index: int, components: list[PathComponent]) -> bool:
    """Check if a separator slash is needed before this component.

    Args:
        index: Index of the current component.
        components: Full list of path components.

    Returns:
        True if a slash separator should be added before this component.
    """
    if index == 0:
        return False
    return components[index - 1].name != "/"


def _append_component(
    result: Text, index: int, comp: PathComponent, components: list[PathComponent]
) -> None:
    """Append a single path component to the result text.

    Handles root "/" specially. Adds separator slash when needed.

    Args:
        result: The Text object to append to.
        index: Index of the current component.
        comp: The path component to append.
        components: Full list of path components.
    """
    color = _get_component_color(comp)
    if index == 0 and comp.name == "/":
        result.append("/", style=color)
        return
    if _needs_separator(index, components):
        prev_color = _get_component_color(components[index - 1])
        result.append("/", style=prev_color)
    result.append(comp.name, style=color)


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
        _append_component(result, i, comp, components)
    return result
