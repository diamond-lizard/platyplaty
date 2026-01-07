"""Rendering helpers for the Pane widget.

This module provides functions for rendering pane content as Strips,
extracted to reduce nesting depth in the Pane class.
"""

from typing import TYPE_CHECKING

from rich.text import Text
from textual.strip import Strip

if TYPE_CHECKING:
    from rich.console import Console


def render_empty_message(
    y: int,
    is_truly_empty: bool,
    width: int,
    console: "Console",
) -> Strip:
    """Render a line for an empty directory.

    Args:
        y: The line number to render (0-indexed).
        is_truly_empty: True if directory had no entries at all,
            False if entries were filtered out.
        width: Width to constrain rendering to, in characters.
        console: Rich console for rendering.

    Returns:
        A Strip containing the rendered line, or empty Strip if y > 0.
    """
    if y != 0:
        return Strip([])
    msg = "empty" if is_truly_empty else "no .milk files"
    text = Text(msg)
    text.truncate(width)
    return Strip(list(text.render(console)))


def render_entry(name: str, width: int, console: "Console") -> Strip:
    """Render a single directory entry.

    Args:
        name: The entry name to display.
        width: Width to constrain rendering to, in characters.
        console: Rich console for rendering.

    Returns:
        A Strip containing the rendered entry.
    """
    text = Text(name)
    text.truncate(width)
    return Strip(list(text.render(console)))
