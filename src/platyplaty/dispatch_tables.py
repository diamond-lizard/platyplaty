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
    add_preset_or_load_playlist_keys: list[str],
    play_previous_preset_keys: list[str],
    play_next_preset_keys: list[str],
) -> DispatchTable:
    """Build dispatch table for file browser navigation key events.

    Args:
        nav_up_keys: List of keys bound to move selection up.
        nav_down_keys: List of keys bound to move selection down.
        nav_left_keys: List of keys bound to navigate to parent.
        nav_right_keys: List of keys bound to navigate into directory.
        add_preset_or_load_playlist_keys: Keys to add preset or load playlist.
        play_previous_preset_keys: Keys to skip to previous preset and play.
        play_next_preset_keys: Keys to skip to next preset and play.

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
    for key in add_preset_or_load_playlist_keys:
        table[key] = "add_preset_or_load_playlist"
    for key in play_previous_preset_keys:
        table[key] = "play_previous_preset"
    for key in play_next_preset_keys:
        table[key] = "play_next_preset"
    return table

def build_global_dispatch_table(
    switch_focus_keys: list[str],
    quit_keys: list[str],
    navigate_up_keys: list[str],
    navigate_down_keys: list[str],
    open_selected_keys: list[str],
    view_errors_keys: list[str],
    play_selection_keys: list[str],
) -> DispatchTable:
    """Build dispatch table for global key events.

    Global keys work regardless of which section has focus.

    Args:
        switch_focus_keys: Keys to switch focus between sections.
        quit_keys: Keys to quit the application.
        navigate_up_keys: Keys to move selection up.
        navigate_down_keys: Keys to move selection down.
        open_selected_keys: Keys to open/enter selected item.
        view_errors_keys: Keys to open error view.
        play_selection_keys: Keys to play selected preset.

    Returns:
        Dispatch table mapping keys to action names.
    """
    table: DispatchTable = {}
    for key in switch_focus_keys:
        table[key] = "switch_focus"
    for key in quit_keys:
        table[key] = "quit"
    for key in navigate_up_keys:
        table[key] = "navigate_up"
    for key in navigate_down_keys:
        table[key] = "navigate_down"
    for key in open_selected_keys:
        table[key] = "open_selected"
    for key in view_errors_keys:
        table[key] = "view_errors"
    for key in play_selection_keys:
        table[key] = "play_selection"
    return table


def build_playlist_dispatch_table(
    play_previous_keys: list[str],
    play_next_keys: list[str],
    reorder_up_keys: list[str],
    reorder_down_keys: list[str],
    delete_keys: list[str],
    undo_keys: list[str],
    redo_keys: list[str],
    save_keys: list[str],
    shuffle_keys: list[str],
    toggle_autoplay_keys: list[str],
    page_up_keys: list[str],
    page_down_keys: list[str],
    navigate_to_first_keys: list[str],
    navigate_to_last_keys: list[str],
) -> DispatchTable:
    """Build dispatch table for playlist section key events.

    Playlist keys only work when the playlist section has focus.

    Args:
        play_previous_keys: Keys to play previous preset.
        play_next_keys: Keys to play next preset.
        reorder_up_keys: Keys to move item up in list.
        reorder_down_keys: Keys to move item down in list.
        delete_keys: Keys to delete preset from playlist.
        undo_keys: Keys to undo last action.
        redo_keys: Keys to redo last undone action.
        save_keys: Keys to save playlist.
        shuffle_keys: Keys to shuffle playlist.
        toggle_autoplay_keys: Keys to toggle autoplay.
        page_up_keys: Keys to move view up one page.
        page_down_keys: Keys to move view down one page.
        navigate_to_first_keys: Keys to go to first preset.
        navigate_to_last_keys: Keys to go to last preset.

    Returns:
        Dispatch table mapping keys to action names.
    """
    table: DispatchTable = {}
    for key in play_previous_keys:
        table[key] = "play_previous"
    for key in play_next_keys:
        table[key] = "play_next"
    for key in reorder_up_keys:
        table[key] = "reorder_up"
    for key in reorder_down_keys:
        table[key] = "reorder_down"
    for key in delete_keys:
        table[key] = "delete_from_playlist"
    for key in undo_keys:
        table[key] = "undo"
    for key in redo_keys:
        table[key] = "redo"
    for key in save_keys:
        table[key] = "save_playlist"
    for key in shuffle_keys:
        table[key] = "shuffle_playlist"
    for key in toggle_autoplay_keys:
        table[key] = "toggle_autoplay"
    for key in page_up_keys:
        table[key] = "page_up"
    for key in page_down_keys:
        table[key] = "page_down"
    for key in navigate_to_first_keys:
        table[key] = "navigate_to_first_preset"
    for key in navigate_to_last_keys:
        table[key] = "navigate_to_last_preset"
    return table


def build_error_view_dispatch_table(
    clear_errors_keys: list[str],
) -> DispatchTable:
    """Build dispatch table for error view key events.

    Error view keys only work when the error view is open.

    Args:
        clear_errors_keys: Keys to clear all errors from log.

    Returns:
        Dispatch table mapping keys to action names.
    """
    table: DispatchTable = {}
    for key in clear_errors_keys:
        table[key] = "clear_errors"
    return table
