#!/usr/bin/env python3
"""Dispatch table builders for keybinding configuration.

Provides functions to build dispatch tables that map key names to action names.
These tables are used by the keybinding dispatch system to route key events.
"""

# Type alias for dispatch tables mapping key names to action names
DispatchTable = dict[str, str]


def build_renderer_dispatch_table(
    next_preset_key: str,
    previous_preset_key: str,
    quit_key: str,
) -> DispatchTable:
    """Build dispatch table for renderer window key events.

    Args:
        next_preset_key: Key bound to next preset action.
        previous_preset_key: Key bound to previous preset action.
        quit_key: Key bound to quit action.

    Returns:
        Dispatch table mapping keys to action names.
    """
    return {
        next_preset_key: "next_preset",
        previous_preset_key: "previous_preset",
        quit_key: "quit",
    }


def build_client_dispatch_table(quit_key: str | None) -> DispatchTable:
    """Build dispatch table for terminal key events.

    Args:
        quit_key: Key bound to quit action, or None if not bound.

    Returns:
        Dispatch table mapping keys to action names.
    """
    table: DispatchTable = {}
    if quit_key is not None:
        table[quit_key] = "quit"
    return table


def build_file_browser_dispatch_table(
    nav_up_keys: list[str],
    nav_down_keys: list[str],
    nav_left_keys: list[str],
    nav_right_keys: list[str],
) -> DispatchTable:
    """Build dispatch table for file browser navigation key events.

    Args:
        nav_up_keys: List of keys bound to move selection up.
        nav_down_keys: List of keys bound to move selection down.
        nav_left_keys: List of keys bound to navigate to parent.
        nav_right_keys: List of keys bound to navigate into directory.

    Returns:
        Dispatch table mapping keys to action names.
    """
    table: DispatchTable = {}
    for key in nav_up_keys:
        table[key] = "nav_up"
    for key in nav_down_keys:
        table[key] = "nav_down"
    for key in nav_left_keys:
        table[key] = "nav_left"
    for key in nav_right_keys:
        table[key] = "nav_right"
    return table
