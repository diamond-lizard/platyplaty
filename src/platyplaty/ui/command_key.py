#!/usr/bin/env python3
"""Key handling for the command prompt."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from textual.app import App

    from platyplaty.ui.command_prompt import CommandPrompt


async def handle_command_key(
    key: str,
    prompt: "CommandPrompt",
    character: str | None,
) -> bool:
    """Handle a key press in the command prompt.

    Args:
        key: The key that was pressed.
        prompt: The CommandPrompt widget instance.
        character: The printable character, or None if not printable.

    Returns:
        True if text or cursor position changed, False otherwise.
    """
    if key in ("escape", "ctrl+c"):
        prompt.hide()
        return False
    if key == "enter":
        if prompt.input_text and prompt.callback:
            await prompt.callback(prompt.input_text)
        else:
            prompt.hide()
        prompt.cursor_index = 0
        return False
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
    if character is not None:
        idx = prompt.cursor_index
        text = prompt.input_text
        prompt.input_text = text[:idx] + character + text[idx:]
        prompt.update_cursor_with_scroll(idx + 1)
        return True
    return False


def return_focus_to_widget(app: "App[object]", widget_id: str | None) -> None:
    """Return focus to a widget by ID.

    Args:
        app: The Textual app instance.
        widget_id: The ID of the widget to focus, or None.
    """
    if not widget_id:
        return
    try:
        widget = app.query_one(f"#{widget_id}")
        widget.focus()
    except Exception:
        pass
