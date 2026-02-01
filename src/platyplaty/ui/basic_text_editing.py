#!/usr/bin/env python3
"""Basic text-editing key handling for command prompts.

This module handles universal text-editing keys (cursor movement, deletion,
character insertion) that are not mode-specific (e.g., not emacs or vi).
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.ui.prompt_interface import PromptInterface


def handle_basic_text_key(
    key: str,
    prompt: "PromptInterface",
    character: str | None,
) -> bool:
    """Handle basic text-editing keys.

    Handles cursor movement (left, right, home, end), deletion (backspace,
    delete), paste (shift+insert), and printable character insertion.

    Args:
        key: The key that was pressed.
        prompt: The prompt interface for text/cursor access.
        character: The printable character, or None if not printable.

    Returns:
        True if text or cursor position changed, False otherwise.
    """
    if key == "left":
        if prompt.cursor_index > 0:
            prompt.update_cursor_with_scroll(prompt.cursor_index - 1)
            return True
        return False
    if key == "right":
        if prompt.cursor_index < len(prompt.input_text):
            prompt.update_cursor_with_scroll(prompt.cursor_index + 1)
            return True
        return False
    if key == "home":
        if prompt.cursor_index > 0:
            prompt.update_cursor_with_scroll(0)
            return True
        return False
    if key == "end":
        text_len = len(prompt.input_text)
        if prompt.cursor_index < text_len:
            prompt.update_cursor_with_scroll(text_len)
            return True
        return False
    if key == "backspace":
        idx = prompt.cursor_index
        if idx > 0:
            prompt.input_text = prompt.input_text[:idx-1] + prompt.input_text[idx:]
            prompt.update_cursor_with_scroll(idx - 1)
            return True
        return False
    if key == "delete":
        idx = prompt.cursor_index
        if idx < len(prompt.input_text):
            prompt.input_text = prompt.input_text[:idx] + prompt.input_text[idx+1:]
            return True
        return False
    if key == "shift+insert":
        return prompt.paste_from_selection()
    if character is not None and character.isprintable():
        idx = prompt.cursor_index
        text = prompt.input_text
        prompt.input_text = text[:idx] + character + text[idx:]
        prompt.update_cursor_with_scroll(idx + 1)
        return True
    return False
