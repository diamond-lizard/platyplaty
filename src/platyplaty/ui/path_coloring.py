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


def get_rendered_length(text: Text) -> int:
    """Calculate the rendered length of a Rich Text object.

    Returns the visible character count excluding ANSI escape codes.

    Args:
        text: Rich Text object to measure.

    Returns:
        Number of visible characters.
    """
    return len(text.plain)


def abbreviate_component(component: PathComponent) -> PathComponent:
    """Abbreviate a path component to its first letter.

    The abbreviated component retains its original type and is_selected flag.

    Args:
        component: The PathComponent to abbreviate.

    Returns:
        New PathComponent with name abbreviated to first letter.
    """
    if not component.name or component.name == "/":
        return component
    abbreviated_name = component.name[0]
    return PathComponent(
        abbreviated_name, component.component_type, component.is_selected
    )


def abbreviate_path_components(
    components: list[PathComponent], max_width: int
) -> list[PathComponent]:
    """Abbreviate path components if the rendered path exceeds max_width.

    All components except the final one are abbreviated to their first letter.
    If the full path fits within max_width, returns the original components.

    Args:
        components: List of PathComponent objects.
        max_width: Maximum allowed width for the rendered path.

    Returns:
        Original components if they fit, otherwise abbreviated components.
    """
    if not components:
        return components
    rendered = render_path_components(components)
    if get_rendered_length(rendered) <= max_width:
        return components
    abbreviated = [
        abbreviate_component(c) if i < len(components) - 1 else c
        for i, c in enumerate(components)
    ]
    return abbreviated
