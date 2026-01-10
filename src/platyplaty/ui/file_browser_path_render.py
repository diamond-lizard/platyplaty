"""Path rendering helpers for the file browser widget.

This module provides helper functions for rendering the path display
line at the top of the file browser.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from rich.segment import Segment

# Re-exported for file_browser_render.py; ruff sees this as unused but it's intentional
from platyplaty.ui.path_orchestrator import render_path  # noqa: F401

__all__ = [
    "render_path",
    "text_to_segments",
    "get_display_path",
    "should_mark_selected",
]


if TYPE_CHECKING:
    from rich.console import Console
    from rich.text import Text

    from platyplaty.ui.file_browser import FileBrowser


def text_to_segments(text: Text, console: Console) -> list[Segment]:
    """Convert Rich Text to a list of Segments.

    Args:
        text: The Rich Text object to convert.
        console: Rich console for rendering.

    Returns:
        A list of Segment objects suitable for use in a Strip.
    """
    return list(text.render(console))


def get_display_path(browser: FileBrowser) -> Path:
    """Get the path to display in the path display line.

    If a file or directory is selected, return current_dir + entry name.
    Otherwise, return just current_dir.

    Args:
        browser: The file browser instance.

    Returns:
        The path to display.
    """
    entry = browser.get_selected_entry()
    if entry is None:
        return browser.current_dir
    return browser.current_dir / entry.name


def should_mark_selected(browser: FileBrowser) -> bool:
    """Determine if the final path component should be marked as selected.

    Returns False when the middle pane is empty or inaccessible (no selectable
    items). In that case, the final component uses its type color rather than
    bright white.

    Args:
        browser: The file browser instance.

    Returns:
        True if final component should be bright white, False otherwise.
    """
    return browser.get_selected_entry() is not None
