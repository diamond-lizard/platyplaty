#!/usr/bin/env python3
"""Application context dataclass for Platyplaty."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from platyplaty.build_dispatch_tables import (
    build_error_view_table,
    build_file_browser_table,
    build_global_table,
    build_playlist_table,
)
from platyplaty.dispatch_tables import DispatchTable
from platyplaty.undo import UndoManager

if TYPE_CHECKING:
    from platyplaty.autoplay_manager import AutoplayManager
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
        current_focus: Which section has focus ("file_browser",
            "playlist", or "error_view").
        autoplay_timer_task: The running autoplay timer task, or None.
        global_dispatch_table: Maps global keys to action names.
        playlist_dispatch_table: Maps playlist keys to action names.
        error_view_dispatch_table: Maps error view keys to action names.
        undo_manager: Manages undo/redo stacks for playlist operations.
        autoplay_manager: Manages autoplay toggle and timer, or None.
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
    undo_manager: UndoManager = field(default_factory=UndoManager)
    autoplay_manager: AutoplayManager | None = None

    def __post_init__(self) -> None:
        """Build dispatch tables from keybindings."""
        kb = self.config.keybindings
        self.file_browser_dispatch_table = build_file_browser_table(kb)
        self.global_dispatch_table = build_global_table(kb)
        self.playlist_dispatch_table = build_playlist_table(kb)
        self.error_view_dispatch_table = build_error_view_table(kb)
