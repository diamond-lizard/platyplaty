#!/usr/bin/env python3
"""UI dispatch table builders for file browser, playlist, and error view.

Provides functions to build dispatch tables for UI section key events.
"""

from platyplaty.dispatch_tables import DispatchTable, _build_table


def build_file_browser_dispatch_table(
    nav_up_keys: list[str],
    nav_down_keys: list[str],
    nav_left_keys: list[str],
    nav_right_keys: list[str],
    add_preset_or_load_playlist_keys: list[str],
    play_previous_preset_keys: list[str],
    play_next_preset_keys: list[str],
) -> DispatchTable:
    """Build dispatch table for file browser navigation key events."""
    return _build_table([
        (nav_up_keys, "nav_up"),
        (nav_down_keys, "nav_down"),
        (nav_left_keys, "nav_left"),
        (nav_right_keys, "nav_right"),
        (add_preset_or_load_playlist_keys, "add_preset_or_load_playlist"),
        (play_previous_preset_keys, "play_previous_preset"),
        (play_next_preset_keys, "play_next_preset"),
    ])


def build_global_dispatch_table(
    switch_focus_keys: list[str],
    quit_keys: list[str],
    navigate_up_keys: list[str],
    navigate_down_keys: list[str],
    open_selected_keys: list[str],
    view_errors_keys: list[str],
    play_selection_keys: list[str],
) -> DispatchTable:
    """Build dispatch table for global key events."""
    return _build_table([
        (switch_focus_keys, "switch_focus"),
        (quit_keys, "quit"),
        (navigate_up_keys, "navigate_up"),
        (navigate_down_keys, "navigate_down"),
        (open_selected_keys, "open_selected"),
        (view_errors_keys, "view_errors"),
        (play_selection_keys, "play_selection"),
    ])


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
    """Build dispatch table for playlist section key events."""
    return _build_table([
        (play_previous_keys, "play_previous"),
        (play_next_keys, "play_next"),
        (reorder_up_keys, "reorder_up"),
        (reorder_down_keys, "reorder_down"),
        (delete_keys, "delete_from_playlist"),
        (undo_keys, "undo"),
        (redo_keys, "redo"),
        (save_keys, "save_playlist"),
        (shuffle_keys, "shuffle_playlist"),
        (toggle_autoplay_keys, "toggle_autoplay"),
        (page_up_keys, "page_up"),
        (page_down_keys, "page_down"),
        (navigate_to_first_keys, "navigate_to_first_preset"),
        (navigate_to_last_keys, "navigate_to_last_preset"),
    ])


def build_error_view_dispatch_table(clear_errors_keys: list[str]) -> DispatchTable:
    """Build dispatch table for error view key events."""
    return _build_table([(clear_errors_keys, "clear_errors")])
