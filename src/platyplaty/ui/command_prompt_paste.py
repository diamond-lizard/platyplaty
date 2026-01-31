#!/usr/bin/env python3
"""Paste behavior for command prompt.

This module provides paste functionality extracted from CommandPrompt
to reduce file size.
"""

from typing import TYPE_CHECKING

from platyplaty.clipboard import get_primary_selection
from platyplaty.ui.paste_handler import handle_paste

if TYPE_CHECKING:
    from platyplaty.ui.command_prompt import CommandPrompt


def do_paste(prompt: "CommandPrompt", text: str) -> bool:
    """Paste text at cursor, stripping whitespace.

    Args:
        prompt: The CommandPrompt widget instance.
        text: Text to paste.

    Returns:
        True if text was inserted, False otherwise.
    """
    result = handle_paste(prompt.input_text, prompt.cursor_index, text)
    if result is None:
        return False
    prompt.input_text, new_cursor = result
    prompt.update_cursor_with_scroll(new_cursor)
    prompt.start_blink_timer()
    return True


def do_paste_from_selection(prompt: "CommandPrompt") -> bool:
    """Paste X11 primary selection at cursor.

    Args:
        prompt: The CommandPrompt widget instance.

    Returns:
        True if text was inserted, False otherwise.
    """
    return do_paste(prompt, get_primary_selection())
