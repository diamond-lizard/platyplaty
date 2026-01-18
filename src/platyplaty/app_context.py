#!/usr/bin/env python3
"""Application context dataclass for Platyplaty."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from platyplaty.dispatch_tables import (
    DispatchTable,
    build_file_browser_dispatch_table,
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

    def __post_init__(self) -> None:
        """Build dispatch tables from keybindings."""
        kb = self.config.keybindings

        # Build file browser dispatch table
        self.file_browser_dispatch_table = build_file_browser_dispatch_table(
            nav_up_keys=kb.globals.navigate_up,
            nav_down_keys=kb.globals.navigate_down,
            nav_left_keys=kb.file_browser.open_parent,
            nav_right_keys=kb.globals.open_selected,
        )
