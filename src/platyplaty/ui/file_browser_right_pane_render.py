"""Right pane rendering functions for the file browser widget.

This module provides functions for rendering individual lines
in the right pane. These are package-private functions.
"""

from rich.segment import Segment
from rich.style import Style

from platyplaty.ui.colors import (
    BACKGROUND_COLOR,
    DIMMED_COLOR,
    EMPTY_MESSAGE_BG,
    EMPTY_MESSAGE_FG,
    FILE_COLOR,
)
from platyplaty.ui.file_browser_file_utils import render_file_preview_line
from platyplaty.ui.file_browser_pane_render import render_pane_line
from platyplaty.ui.file_browser_types import (
    RightPaneBinaryFile,
    RightPaneContent,
    RightPaneDirectory,
    RightPaneEmpty,
    RightPaneFilePreview,
    RightPaneNoMilk,
)


def _render_special_message(
    content: RightPaneEmpty | RightPaneNoMilk | RightPaneBinaryFile,
    y: int,
    width: int,
) -> list[Segment]:
    """Render special message (empty, no milk, binary) for right pane."""
    bg_style = Style(bgcolor=BACKGROUND_COLOR)
    if y != 0:
        return [Segment(" " * width, bg_style)]
    if isinstance(content, RightPaneEmpty):
        msg = "empty"
    elif isinstance(content, RightPaneNoMilk):
        msg = "no .milk files"
    else:
        msg = "BINARY FILE"
    text = msg.ljust(width)[:width]
    style = Style(color=EMPTY_MESSAGE_FG, bgcolor=EMPTY_MESSAGE_BG)
    return [Segment(text, style)]

def render_right_pane_line(
    content: RightPaneContent, y: int, width: int,
    scroll_offset: int = 0, selected_index: int | None = None, focused: bool = True,
) -> list[Segment]:
    """Render a single line of the right pane.

    Handles both directory listings and file previews.

    Args:
        content: The right pane content to render.
        y: The line number to render (0-indexed).
        width: The width of the pane.
        scroll_offset: Offset into the listing for scrolling (default 0).
        selected_index: Index of selected item for highlighting (None for no selection).

    Returns:
        A list of Segments with appropriate styling.
    """
    bg_style = Style(bgcolor=BACKGROUND_COLOR)
    if content is None:
        return [Segment(" " * width, bg_style)]
    if isinstance(content, RightPaneDirectory):
        return render_pane_line(
            content.listing, y, width, is_left_pane=False,
            scroll_offset=scroll_offset, selected_index=selected_index,
            show_indicators=False, focused=focused,
        )
    if isinstance(content, (RightPaneEmpty, RightPaneNoMilk, RightPaneBinaryFile)):
        return _render_special_message(content, y, width)
    if isinstance(content, RightPaneFilePreview):
        text = render_file_preview_line(content.lines, y, width)
        color = FILE_COLOR if focused else DIMMED_COLOR
        style = Style(color=color, bgcolor=BACKGROUND_COLOR)
        return [Segment(text, style)]
    # RightPanePlaylistPreview - placeholder until Phase 400 implements
    return [Segment(" " * width, Style(bgcolor=BACKGROUND_COLOR))]
