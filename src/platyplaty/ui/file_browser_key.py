"""Key handling functions for the file browser widget.

This module provides functions for handling key events in the
file browser. This is a package-private module used by the
FileBrowser class.
"""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Any

from textual.events import Key

from platyplaty.ui.file_browser_nav import action_nav_left, action_nav_right
from platyplaty.ui.file_browser_nav_updown import action_nav_down, action_nav_up
from platyplaty.ui.file_browser_actions import action_add_preset_or_load_playlist

if TYPE_CHECKING:
    from platyplaty.ui.file_browser import FileBrowser


ActionFunc = Callable[["FileBrowser"], Coroutine[Any, Any, None]]

async def on_key(browser: FileBrowser, event: Key) -> None:
    """Handle key events for file browser navigation.

    Looks up the key in the dispatch table and calls the action function.

    Args:
        browser: The file browser instance.
        event: The key event from Textual.
    """
    if not browser.has_focus:
        return
    action_name = browser._dispatch_table.get(event.key)
    if action_name is None:
        return
    action_func = _get_action_func(action_name)
    if action_func is not None:
        await action_func(browser)
        event.prevent_default()


def _get_action_func(action_name: str) -> ActionFunc | None:
    """Get the action function for a given action name.

    Args:
        action_name: The name of the action (e.g., "nav_up").

    Returns:
        The action function, or None if not found.
    """
    actions = {
        "nav_up": action_nav_up,
        "nav_down": action_nav_down,
        "nav_left": action_nav_left,
        "nav_right": action_nav_right,
        "add_preset_or_load_playlist": action_add_preset_or_load_playlist,
    }
    return actions.get(action_name)
