#!/usr/bin/env python3
"""Textual application for Platyplaty visualizer control."""

from typing import TYPE_CHECKING

from textual.app import App, ComposeResult
from textual.events import Key
from textual.widgets import RichLog, Static

from platyplaty.app_actions import load_preset_by_direction
from platyplaty.app_context import AppContext
from platyplaty.app_shutdown import perform_graceful_shutdown
from platyplaty.app_startup import (
    cleanup_on_startup_failure,
    perform_startup,
    setup_signal_handlers,
)
from platyplaty.keybinding_dispatch import dispatch_key_event
from platyplaty.ui import FileBrowser, TransientErrorBar

if TYPE_CHECKING:
    import asyncio

    from platyplaty.messages import LogMessage
    from platyplaty.playlist import Playlist
    from platyplaty.socket_client import SocketClient
    from platyplaty.types.app_config import AppConfig
    from platyplaty.types.keybindings import FileBrowserKeybindings
    from platyplaty.types.renderer_keybindings import (
        ClientKeybindings,
        RendererKeybindings,
    )


class PlatyplatyApp(App[None]):
    """Textual application for controlling the Platyplaty visualizer.

    This app manages the renderer process, handles keyboard input from both
    the terminal and the renderer window, and coordinates auto-advance and
    other background tasks.

    Attributes:
        renderer_dispatch_table: Maps renderer window keys to action names.
        client_dispatch_table: Maps terminal keys to action names.
        _renderer_ready: True after INIT command succeeds.
    """

    CSS = """
    #file_browser {
        height: 70%;
    }
    #log {
        height: 30%;
    }
    """

    ctx: "AppContext"
    renderer_dispatch_table: dict[str, str]
    client_dispatch_table: dict[str, str]
    file_browser_dispatch_table: dict[str, str]
    _renderer_ready: bool
    _exiting: bool
    _renderer_process: "asyncio.subprocess.Process | None"
    _client: "SocketClient | None"
    playlist: "Playlist"
    preset_duration: float
    fullscreen: bool
    socket_path: str
    audio_source: str
    _client_keybindings: "ClientKeybindings"
    _renderer_keybindings: "RendererKeybindings"
    _file_browser_keybindings: "FileBrowserKeybindings"


    def __init__(
        self,
        config: "AppConfig",
        playlist: "Playlist",
    ) -> None:
        """Initialize the Platyplaty application.

        Args:
            config: Immutable application configuration.
            playlist: The playlist instance for preset navigation.
        """
        super().__init__()

        # Create AppContext which builds dispatch tables in __post_init__
        self.ctx = AppContext(config=config, playlist=playlist)

        # Backward compatibility: expose attributes directly on app
        self.socket_path = config.socket_path
        self.audio_source = config.audio_source
        self.playlist = playlist
        self.preset_duration = config.preset_duration
        self.fullscreen = config.fullscreen
        self._client_keybindings = config.keybindings.client
        self._renderer_keybindings = config.keybindings.renderer
        self._file_browser_keybindings = config.keybindings.file_browser
        self._exiting = False
        self._renderer_process = None
        self._renderer_ready = False
        self._client = None

        # Build dispatch tables for backward compatibility
        # (These are also available via self.ctx.*_dispatch_table)
        self.renderer_dispatch_table = self.ctx.renderer_dispatch_table
        self.client_dispatch_table = self.ctx.client_dispatch_table
        self.file_browser_dispatch_table = self.ctx.file_browser_dispatch_table



    def compose(self) -> ComposeResult:
        """Create child widgets for the application.

        Returns:
            Widgets to mount in the application.
        """
        yield Static("Platyplaty Visualizer", id="status")
        yield FileBrowser(self.file_browser_dispatch_table, id="file_browser")
        yield RichLog(id="log")
        yield TransientErrorBar(id="transient_error")


    async def on_mount(self) -> None:
        """Perform startup sequence when the app is mounted.

        Delegates to app_startup module for signal handlers and startup
        sequence. On failure, cleans up and exits with error message.
        """
        setup_signal_handlers(self)
        try:
            await perform_startup(self.ctx, self)
        except Exception as e:
            await cleanup_on_startup_failure(self.ctx)
            self.exit(message=str(e))

    async def action_quit(self) -> None:
        """Quit the application gracefully.

        Sends QUIT command to renderer and closes connections.
        """
        await self.graceful_shutdown()

    async def action_next_preset(self) -> None:
        """Advance to the next preset in the playlist."""
        await load_preset_by_direction(self.ctx, self, self.playlist.next, "next")

    async def action_previous_preset(self) -> None:
        """Go back to the previous preset in the playlist."""
        await load_preset_by_direction(
            self.ctx, self, self.playlist.previous, "previous"
        )

    async def graceful_shutdown(self) -> None:
        """Shut down the application gracefully."""
        await perform_graceful_shutdown(self.ctx, self)

    async def on_key(self, event: Key) -> None:
        """Handle terminal key events.

        Dispatches key events to actions via the client dispatch table.

        Args:
            event: The key event from Textual.
        """
        await dispatch_key_event(event.key, self.client_dispatch_table, self)

    def on_log_message(self, message: "LogMessage") -> None:
        """Handle log messages by writing to the RichLog widget.

        Args:
            message: The log message to display.
        """
        log_widget = self.query_one("#log", RichLog)
        log_widget.write(message.text)
