"""Main rendering function for the file browser widget.

This module provides the render_line function that composes all three
panes into a single line. It is a package-private function used by
the FileBrowser class.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from pathlib import Path

from rich.segment import Segment
from textual.strip import Strip

from platyplaty.ui.file_browser_pane_render import (
    render_pane_line,
    render_right_pane_line,
)
from platyplaty.ui.layout import calculate_pane_widths
from platyplaty.ui.path_orchestrator import render_path

if TYPE_CHECKING:
    from platyplaty.ui.file_browser import FileBrowser
    from rich.console import Console
    from rich.text import Text


def text_to_segments(text: Text, console: "Console") -> list[Segment]:
    """Convert Rich Text to a list of Segments.

    Args:
        text: The Rich Text object to convert.
        console: Rich console for rendering.

    Returns:
        A list of Segment objects suitable for use in a Strip.
    """
    return list(text.render(console))

def _get_display_path(browser: "FileBrowser") -> Path:
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

def _should_mark_selected(browser: "FileBrowser") -> bool:
    """Determine if the final path component should be marked as selected.

    Returns False when the middle pane is empty or inaccessible (no selectable
    items). In that case, per REQ-0700, the final component uses its type color
    rather than bright white.

    Args:
        browser: The file browser instance.

    Returns:
        True if final component should be bright white, False otherwise.
    """
    return browser.get_selected_entry() is not None

def render_line(browser: FileBrowser, y: int) -> Strip:
    """Render a single line of the file browser.

    Args:
        browser: The file browser instance.
        y: The line number to render (0-indexed).

    Returns:
        A Strip containing the rendered line.
    """
    width = browser.size.width
    # y=0 is the path display line
    if y == 0:
        path = _get_display_path(browser)
        mark_selected = _should_mark_selected(browser)
        path_text = render_path(path, width, mark_selected)
        segments = text_to_segments(path_text, browser.app.console)
        return Strip(segments)

    pane_widths = calculate_pane_widths(width)
    pane_y = y - 1  # Panes start at y=1, so subtract 1

    segments: list[Segment] = []

    # Render left pane
    if pane_widths.left > 0:
        left_text = render_pane_line(
            browser._left_listing, pane_y, pane_widths.left, is_left_pane=True,
            scroll_offset=browser._left_scroll_offset
        )
        segments.append(Segment(left_text))
        segments.append(Segment(" "))  # Gap

    # Render middle pane
    middle_text = render_pane_line(
        browser._middle_listing, pane_y, pane_widths.middle,
        is_left_pane=False, scroll_offset=browser._middle_scroll_offset
    )
    segments.append(Segment(middle_text))
    segments.append(Segment(" "))  # Gap

    # Render right pane
    right_text = render_right_pane_line(browser._right_content, pane_y, pane_widths.right)
    segments.append(Segment(right_text))

    return Strip(segments)
