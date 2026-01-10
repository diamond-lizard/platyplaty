#!/usr/bin/env python3
"""Path truncation functions for file browser path display.

This module provides functions to truncate the final path component
when the abbreviated path still exceeds the terminal width.
"""

from platyplaty.ui.path_types import PathComponent
from platyplaty.ui.path_abbreviation import get_rendered_length
from platyplaty.ui.path_coloring import render_path_components


def truncate_final_component(component: PathComponent, max_length: int) -> PathComponent:
    """Truncate a path component to fit within max_length characters.

    Uses simple right truncation with tilde (~) indicator.
    Ensures at least 1 character of the name plus tilde is shown.

    Args:
        component: The PathComponent to truncate.
        max_length: Maximum length for the component name.

    Returns:
        New PathComponent with truncated name, or original if it fits.
    """
    if len(component.name) <= max_length:
        return component
    if max_length < 2:
        truncated_name = component.name[0] + "~" if component.name else "~"
    else:
        truncated_name = component.name[: max_length - 1] + "~"
    return PathComponent(
        truncated_name, component.component_type, component.is_selected
    )

def truncate_abbreviated_path(
    components: list[PathComponent], max_width: int
) -> list[PathComponent]:
    """Truncate the final component of an abbreviated path if needed.

    Given components that have already been abbreviated (all except final
    reduced to first letter), truncates the final component if the total
    rendered length still exceeds max_width.

    Args:
        components: List of PathComponent objects (already abbreviated).
        max_width: Maximum available width in characters.

    Returns:
        List with final component truncated if necessary.
    """
    if not components:
        return components
    rendered = render_path_components(components)
    if get_rendered_length(rendered) <= max_width:
        return components
    prefix = components[:-1]
    prefix_rendered = render_path_components(prefix)
    prefix_length = get_rendered_length(prefix_rendered)
    if prefix:
        prefix_length += 1
    available = max_width - prefix_length
    if available < 2:
        available = 2
    truncated_final = truncate_final_component(components[-1], available)
    return prefix + [truncated_final]
