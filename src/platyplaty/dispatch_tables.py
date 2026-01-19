#!/usr/bin/env python3
"""Dispatch table builders for keybinding configuration.

Provides functions to build dispatch tables that map key names to action names.
These tables are used by the keybinding dispatch system to route key events.
"""

# Type alias for dispatch tables mapping key names to action names
DispatchTable = dict[str, str]


def _build_table(mappings: list[tuple[list[str], str]]) -> DispatchTable:
    """Build dispatch table from key-action mappings.

    Args:
        mappings: List of (keys, action_name) tuples.

    Returns:
        Dispatch table mapping each key to its action name.
    """
    table: DispatchTable = {}
    for keys, action in mappings:
        for key in keys:
            table[key] = action
    return table


def build_renderer_dispatch_table(
    next_preset_key: str,
    previous_preset_key: str,
    quit_key: str,
) -> DispatchTable:
    """Build dispatch table for renderer window key events."""
    return {
        next_preset_key: "next_preset",
        previous_preset_key: "previous_preset",
        quit_key: "quit",
    }


def build_client_dispatch_table(quit_key: str | None) -> DispatchTable:
    """Build dispatch table for terminal key events."""
    if quit_key is None:
        return {}
    return {quit_key: "quit"}
