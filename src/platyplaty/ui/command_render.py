#!/usr/bin/env python3
"""Rendering logic for the command prompt widget.

This module provides the render function for displaying the command prompt
with cursor, handling horizontal scrolling and cursor visibility.
"""

from rich.segment import Segment
from rich.style import Style
from rich.strip import Strip

from platyplaty.ui.style_utils import reverse_style

PROMPT_STYLE = Style(color="white", bgcolor="black")
CURSOR_STYLE = reverse_style(PROMPT_STYLE)
BLINK_INTERVAL_MS = 500


def render_command_line(
    width: int,
    input_text: str,
    text_scroll: int,
    cursor_index: int,
    cursor_visible: bool,
) -> Strip:
    """Render a single line of the command prompt.

    Args:
        width: Total widget width in characters.
        input_text: The current input text.
        text_scroll: Horizontal scroll offset for the input text.
        cursor_index: Position of the cursor in the input text.
        cursor_visible: Whether the cursor should be rendered.

    Returns:
        A Strip containing the rendered segments.
    """
    visible_width = width - 1  # Account for ":" prefix
    if visible_width < 0:
        visible_width = 0
    end = text_scroll + visible_width
    visible_text = input_text[text_scroll:end]
    cursor_pos = cursor_index - text_scroll
    segments: list[Segment] = [Segment(":", PROMPT_STYLE)]
    if not cursor_visible or cursor_pos < 0 or cursor_pos > len(visible_text):
        segments.append(Segment(visible_text.ljust(visible_width), PROMPT_STYLE))
    else:
        before = visible_text[:cursor_pos]
        if cursor_pos < len(visible_text):
            cursor_char = visible_text[cursor_pos]
            after = visible_text[cursor_pos + 1 :]
        else:
            cursor_char = " "
            after = ""
        segments.append(Segment(before, PROMPT_STYLE))
        segments.append(Segment(cursor_char, CURSOR_STYLE))
        remaining = visible_width - len(before) - 1 - len(after)
        segments.append(Segment(after + " " * max(0, remaining), PROMPT_STYLE))
    return Strip(segments)


def calculate_scroll_offset(
    cursor_pos: int,
    current_scroll: int,
    visible_width: int,
) -> int:
    """Calculate scroll offset to keep cursor visible.

    Args:
        cursor_pos: The cursor position in the input text.
        current_scroll: The current scroll offset.
        visible_width: The visible width for the input text.

    Returns:
        The new scroll offset.
    """
    if visible_width < 1:
        visible_width = 1
    if cursor_pos > current_scroll + visible_width - 1:
        return cursor_pos - visible_width + 1
    if cursor_pos < current_scroll:
        return cursor_pos
    return current_scroll
