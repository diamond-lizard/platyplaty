#!/usr/bin/env python3
"""Application context dataclass for Platyplaty."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from platyplaty.dispatch_tables import (
    DispatchTable,
    build_error_view_dispatch_table,
    build_file_browser_dispatch_table,
    build_global_dispatch_table,
    build_playlist_dispatch_table,
)

if TYPE_CHECKING:
    from platyplaty.playlist import Playlist
    from platyplaty.socket_client import SocketClient
    from platyplaty.types.app_config import AppConfig


@dataclass
class AppContext:
    """Mutable application runtime state.

    Contains all runtime state for the application. This is passed to
    functions that need access to application state without requiring
    access to the Textual App object itself.

    Attributes:
        config: Immutable application configuration.
        playlist: The playlist instance for preset navigation.
        client: Socket client for renderer communication, or None.
        renderer_process: The renderer subprocess, or None.
        renderer_ready: True after INIT command succeeds.
        exiting: True when graceful shutdown is in progress.
        renderer_dispatch_table: Maps renderer window keys to action names.
        client_dispatch_table: Maps terminal keys to action names.
        file_browser_dispatch_table: Maps file browser keys to action names.
        error_log: List of renderer error messages for later viewing.
        current_focus: Which section has focus ("file_browser", "playlist", or "error_view").
        autoplay_timer_task: The running autoplay timer task, or None.
        global_dispatch_table: Maps global keys to action names.
        playlist_dispatch_table: Maps playlist keys to action names.
        error_view_dispatch_table: Maps error view keys to action names.
    """

    config: AppConfig
    playlist: Playlist
    client: SocketClient | None = None
    renderer_process: asyncio.subprocess.Process | None = None
    renderer_ready: bool = False
    exiting: bool = False
    renderer_dispatch_table: DispatchTable = field(default_factory=dict)
    client_dispatch_table: DispatchTable = field(default_factory=dict)
    file_browser_dispatch_table: DispatchTable = field(default_factory=dict)
    error_log: list[str] = field(default_factory=list)
    current_focus: str = "file_browser"
    autoplay_timer_task: asyncio.Task[None] | None = None
    global_dispatch_table: DispatchTable = field(default_factory=dict)
    playlist_dispatch_table: DispatchTable = field(default_factory=dict)
    error_view_dispatch_table: DispatchTable = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Build dispatch tables from keybindings."""
        kb = self.config.keybindings

        # Build file browser dispatch table
        self.file_browser_dispatch_table = build_file_browser_dispatch_table(
            nav_up_keys=kb.globals.navigate_up,
            nav_down_keys=kb.globals.navigate_down,
            nav_left_keys=kb.file_browser.open_parent,
            nav_right_keys=kb.globals.open_selected,
            add_preset_or_load_playlist_keys=kb.file_browser.add_preset_or_load_playlist,
            play_previous_preset_keys=kb.file_browser.play_previous_preset,
            play_next_preset_keys=kb.file_browser.play_next_preset,
        )

        # Build global dispatch table
        self.global_dispatch_table = build_global_dispatch_table(
            switch_focus_keys=kb.globals.switch_focus,
            quit_keys=kb.globals.quit,
            navigate_up_keys=kb.globals.navigate_up,
            navigate_down_keys=kb.globals.navigate_down,
            open_selected_keys=kb.globals.open_selected,
            view_errors_keys=kb.globals.view_errors,
            play_selection_keys=kb.globals.play_selection,
        )

        # Build playlist dispatch table
        self.playlist_dispatch_table = build_playlist_dispatch_table(
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

        # Build error view dispatch table
        self.error_view_dispatch_table = build_error_view_dispatch_table(
            clear_errors_keys=kb.error_view.clear_errors,
        )
