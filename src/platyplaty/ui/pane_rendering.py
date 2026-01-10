"""Rendering helpers for the Pane widget.

This module provides functions for rendering pane content as Strips,
extracted to reduce nesting depth in the Pane class.
"""

from typing import TYPE_CHECKING

from rich.text import Text
from rich.style import Style
from textual.strip import Strip
from platyplaty.ui.colors import BACKGROUND_COLOR, get_entry_color

if TYPE_CHECKING:
    from rich.console import Console
    from platyplaty.ui.directory_types import DirectoryEntry


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


def render_entry(entry: "DirectoryEntry", width: int, console: "Console") -> Strip:
    """Render a single directory entry with appropriate colors.

    Args:
        entry: The directory entry to display.
        width: Width to constrain rendering to, in characters.
        console: Rich console for rendering.

    Returns:
        A Strip containing the rendered entry with color styling.
    """
    color = get_entry_color(entry.entry_type)
    style = Style(color=color, bgcolor=BACKGROUND_COLOR)
    text = Text(entry.name, style=style)
    text.truncate(width)
    return Strip(list(text.render(console)))
