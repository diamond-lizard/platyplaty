#!/usr/bin/env python3
"""Key handling for confirmation prompts."""

from collections.abc import Awaitable, Callable


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

