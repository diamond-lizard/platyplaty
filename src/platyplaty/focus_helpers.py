#!/usr/bin/env python3
"""Focus helper utilities for Platyplaty.

Provides functions to determine widget IDs based on application focus state.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app_context import AppContext


def get_previous_focus_id(ctx: "AppContext") -> str | None:
    """Get the widget ID for the currently focused section.

    Used to restore Textual widget focus after prompts are dismissed.

    Args:
        ctx: Application context with current_focus.

    Returns:
        Widget ID string for the focused section, or None if unknown.
    """
    if ctx.current_focus == "file_browser":
        return "file_browser"
    if ctx.current_focus == "playlist":
        return "playlist"
    return None
