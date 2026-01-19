#!/usr/bin/env python3
"""Key handling for the command prompt."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from textual.app import App

    from platyplaty.ui.command_prompt import CommandPrompt


async def handle_command_key(key: str, prompt: "CommandPrompt") -> None:
    """Handle a key press in the command prompt.

    Args:
        key: The key that was pressed.
        prompt: The CommandPrompt widget instance.
    """
    if key == "escape":
        prompt.hide()
        return
    if key == "enter":
        if prompt.input_text and prompt.callback:
            await prompt.callback(prompt.input_text)
        else:
            prompt.hide()
        return
    if key == "backspace":
        prompt.input_text = prompt.input_text[:-1]
        return
    if len(key) == 1 and key.isprintable():
        prompt.input_text += key


def return_focus_to_widget(app: "App", widget_id: str | None) -> None:
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
