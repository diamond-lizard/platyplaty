#!/usr/bin/env python3
"""Path rendering orchestrator for file browser path display.

This module provides the orchestrator function that implements the
complete path rendering algorithm, coordinating abbreviation, fallback,
and truncation as needed to fit the path within the terminal width.
"""

from pathlib import Path

from rich.text import Text

from platyplaty.ui.path_abbreviation import (
    abbreviate_path_components,
    get_rendered_length,
)
from platyplaty.ui.path_coloring import render_path_components
from platyplaty.ui.path_display import split_path_to_components
from platyplaty.ui.path_fallback import (
    fallback_path_components,
    prefix_exceeds_width,
)
from platyplaty.ui.path_truncation import truncate_abbreviated_path
from platyplaty.ui.path_types import PathComponent


def render_path(
    path: Path | str, width: int, mark_selected: bool = True
) -> Text:
    """Render a path for display, fitting within the given width.

    Implements the runtime algorithm from Section 1a:
    1. Try full path
    2. If too long, abbreviate all but final component
    3. If still too long and prefix fits, truncate final
    4. If prefix exceeds width, fall back to full components from root

    Args:
        path: The path to render.
        width: Maximum width in characters.
        mark_selected: If True, mark final component as selected.

    Returns:
        Rich Text object with styled path.
    """
    components = split_path_to_components(path, mark_selected)
    return _render_components(components, width)


def _render_components(components: list[PathComponent], width: int) -> Text:
    """Render path components, applying abbreviation/truncation as needed.

    Args:
        components: List of PathComponent objects.
        width: Maximum width in characters.

    Returns:
        Rich Text object with styled path.
    """
    if not components:
        return Text()
    full_rendered = render_path_components(components)
    if get_rendered_length(full_rendered) <= width:
        return full_rendered
    abbreviated = abbreviate_path_components(components, width)
    abbreviated_rendered = render_path_components(abbreviated)
    if get_rendered_length(abbreviated_rendered) <= width:
        return abbreviated_rendered
    if prefix_exceeds_width(abbreviated, width):
        fallback = fallback_path_components(components, width)
        return render_path_components(fallback)
    truncated = truncate_abbreviated_path(abbreviated, width)
    return render_path_components(truncated)
