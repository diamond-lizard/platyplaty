#!/usr/bin/env python3
"""Key handling for confirmation prompts."""

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from textual.app import App


async def handle_confirmation_key(
    key: str,
    callback: Callable[[bool], Awaitable[None]] | None,
    hide_func: Callable[[], None],
) -> bool:
    """Handle a key press in a confirmation prompt.

    Args:
        key: The key that was pressed.
        callback: Async function to call with result (True/False).
        hide_func: Function to call to hide the prompt.

    Returns:
        True if the key was y or n (handled), False otherwise (ignored).
    """
    key_lower = key.lower()
    if key_lower == "y":
        hide_func()
        if callback:
            await callback(True)
        return True
    if key_lower == "n":
        hide_func()
        if callback:
            await callback(False)
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
