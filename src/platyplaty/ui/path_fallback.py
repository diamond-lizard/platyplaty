#!/usr/bin/env python3
"""Path fallback functions for file browser path display.

This module provides functions to handle fallback display when the
abbreviated path prefix exceeds the terminal width.
"""


from platyplaty.ui.path_abbreviation import abbreviate_component, get_rendered_length
from platyplaty.ui.path_coloring import render_path_components
from platyplaty.ui.path_types import PathComponent


def get_prefix_length(components: list[PathComponent]) -> int:
    """Calculate rendered length of path prefix (all except final component).

    The prefix includes all components except the final one, plus any
    separating slashes that would appear between them.

    Args:
        components: List of PathComponent objects.

    Returns:
        Rendered length of the prefix in characters.
    """
    if len(components) <= 1:
        return 0
    prefix_components = components[:-1]
    rendered = render_path_components(prefix_components)
    return get_rendered_length(rendered)


def prefix_exceeds_width(components: list[PathComponent], max_width: int) -> bool:
    """Check if abbreviated prefix alone exceeds the maximum width.

    This function first abbreviates all components except the final one,
    then checks if the resulting prefix exceeds the available width.
    Also returns True if the prefix would leave fewer than 2 characters
    for the final component (minimum: 1 char + tilde).

    Args:
        components: List of PathComponent objects.
        max_width: Maximum available width in characters.

    Returns:
        True if abbreviated prefix exceeds width or leaves < 2 chars for final.
    """
    if len(components) <= 1:
        return False
    abbreviated = [abbreviate_component(c) for c in components[:-1]]
    prefix_length = get_prefix_length(abbreviated + [components[-1]])
    remaining = max_width - prefix_length
    return prefix_length > max_width or remaining < 2


def fallback_path_components(
    components: list[PathComponent], max_width: int
) -> list[PathComponent]:
    """Get fallback path showing full components from root that fit.

    When the abbreviated prefix exceeds the available width, this function
    returns as many full (unabbreviated) path components from root as will
    fit. The final component (selected item) is not included.

    Args:
        components: List of PathComponent objects.
        max_width: Maximum available width in characters.

    Returns:
        List of full path components from root that fit within max_width.
    """
    if not components:
        return []
    result: list[PathComponent] = []
    for comp in components[:-1]:
        candidate = result + [comp]
        rendered = render_path_components(candidate)
        if get_rendered_length(rendered) > max_width:
            break
        result = candidate
    if not result and components:
        root = components[0]
        if root.name == "/":
            result = [root]
    return result
