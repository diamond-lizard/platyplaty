#!/usr/bin/env python3
"""Path abbreviation functions for file browser path display.

This module provides functions to abbreviate path components when
the path is too long to fit in the available width.
"""

from rich.text import Text

from platyplaty.ui.path_coloring import render_path_components
from platyplaty.ui.path_types import PathComponent


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
