#!/usr/bin/env python3
"""Build dispatch tables from keybindings configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from platyplaty.dispatch_tables import DispatchTable
from platyplaty.dispatch_tables_ui import (
    build_error_view_dispatch_table,
    build_file_browser_dispatch_table,
    build_global_dispatch_table,
    build_playlist_dispatch_table,
)

if TYPE_CHECKING:
    from platyplaty.types.keybindings import Keybindings


def build_file_browser_table(kb: Keybindings) -> DispatchTable:
    """Build file browser dispatch table from keybindings."""
    return build_file_browser_dispatch_table(
        nav_up_keys=kb.globals.navigate_up,
        nav_down_keys=kb.globals.navigate_down,
        nav_left_keys=kb.file_browser.open_parent,
        nav_right_keys=kb.globals.open_selected,
        add_preset_or_load_playlist_keys=kb.file_browser.add_preset_or_load_playlist,
        play_previous_preset_keys=kb.file_browser.play_previous_preset,
        play_next_preset_keys=kb.file_browser.play_next_preset,
    )


def build_global_table(kb: Keybindings) -> DispatchTable:
    """Build global dispatch table from keybindings."""
    return build_global_dispatch_table(
        switch_focus_keys=kb.globals.switch_focus,
        quit_keys=kb.globals.quit,
        navigate_up_keys=kb.globals.navigate_up,
        navigate_down_keys=kb.globals.navigate_down,
        open_selected_keys=kb.globals.open_selected,
        view_errors_keys=kb.globals.view_errors,
        play_selection_keys=kb.globals.play_selection,
    )


def build_playlist_table(kb: Keybindings) -> DispatchTable:
    """Build playlist dispatch table from keybindings."""
    return build_playlist_dispatch_table(
        play_previous_keys=kb.playlist.play_previous,
        play_next_keys=kb.playlist.play_next,
        reorder_up_keys=kb.playlist.reorder_up,
        reorder_down_keys=kb.playlist.reorder_down,
        delete_keys=kb.playlist.delete_from_playlist,
        undo_keys=kb.playlist.undo,
        redo_keys=kb.playlist.redo,
        save_keys=kb.playlist.save_playlist,
        shuffle_keys=kb.playlist.shuffle_playlist,
        toggle_autoplay_keys=kb.playlist.toggle_autoplay,
        page_up_keys=kb.playlist.page_up,
        page_down_keys=kb.playlist.page_down,
        navigate_to_first_keys=kb.playlist.navigate_to_first_preset,
        navigate_to_last_keys=kb.playlist.navigate_to_last_preset,
    )


def build_error_view_table(kb: Keybindings) -> DispatchTable:
    """Build error view dispatch table from keybindings."""
    return build_error_view_dispatch_table(
        clear_errors_keys=kb.error_view.clear_errors,
    )
