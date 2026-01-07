#!/usr/bin/env python3
"""Textual application for Platyplaty visualizer control."""

import asyncio
import signal
from typing import TYPE_CHECKING

from textual.app import App, ComposeResult
from textual.widgets import RichLog, Static
from textual.events import Key

from platyplaty.messages import LogMessage
from platyplaty.socket_client import RendererError, SocketClient
from platyplaty.auto_advance import auto_advance_loop, load_preset_with_retry
from platyplaty.event_loop import stderr_monitor_task
from platyplaty.keybinding_dispatch import (
    build_client_dispatch_table,
    dispatch_key_event,
    build_renderer_dispatch_table,
    build_file_browser_dispatch_table,
)
from platyplaty.renderer import start_renderer
from platyplaty.ui import FileBrowser, TransientErrorBar

if TYPE_CHECKING:
    from platyplaty.playlist import Playlist
    from platyplaty.types.config import FileBrowserKeybindings


class PlatyplatyApp(App):
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

    renderer_dispatch_table: dict[str, str]
    client_dispatch_table: dict[str, str]
    _renderer_ready: bool
    _exiting: bool
    _renderer_process: asyncio.subprocess.Process | None
    _client: SocketClient | None
    playlist: "Playlist"
    preset_duration: float
    fullscreen: bool
    socket_path: str
    audio_source: str
    _client_keybindings: dict[str, str]
    _renderer_keybindings: dict[str, str]
    _file_browser_keybindings: "FileBrowserKeybindings"


    def __init__(
        self,
        socket_path: str,
        audio_source: str,
        playlist: "Playlist",
        preset_duration: float,
        fullscreen: bool,
        client_keybindings: dict[str, str],
        renderer_keybindings: dict[str, str],
        file_browser_keybindings: "FileBrowserKeybindings",
    ) -> None:
        """Initialize the Platyplaty application.

        Args:
            socket_path: Path to the Unix domain socket.
            audio_source: PulseAudio source for audio capture.
            playlist: The playlist instance for preset navigation.
            preset_duration: Seconds to display each preset.
            fullscreen: Whether to start in fullscreen mode.
            client_keybindings: Keybindings for terminal input.
            renderer_keybindings: Keybindings for renderer window input.
        """
        super().__init__()
        self.socket_path = socket_path
        self.audio_source = audio_source
        self.playlist = playlist
        self.preset_duration = preset_duration
        self.fullscreen = fullscreen
        self._client_keybindings = client_keybindings
        self._renderer_keybindings = renderer_keybindings
        self._file_browser_keybindings = file_browser_keybindings
        self._exiting = False
        self._renderer_process = None
        self._renderer_ready = False
        self._client = None

        # Build file browser dispatch table (available in compose)
        self.file_browser_dispatch_table = build_file_browser_dispatch_table(
            nav_up_keys=self._file_browser_keybindings.nav_up,
            nav_down_keys=self._file_browser_keybindings.nav_down,
            nav_left_keys=self._file_browser_keybindings.nav_left,
            nav_right_keys=self._file_browser_keybindings.nav_right,
        )

        # Build client dispatch table for app-level actions
        self.client_dispatch_table = build_client_dispatch_table(
            quit_key=self._client_keybindings.quit,
        )
        self.client_dispatch_table["ctrl+c"] = "quit"



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

        Stage A: Start renderer, connect socket, send initial commands.
        Stage B: Start background workers.
        Stage C: Show window and optionally go fullscreen.

        On startup error, terminates renderer if started, closes client
        if connected, and exits with error message.
        """
        # Register signal handlers for external SIGINT/SIGTERM
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(
            signal.SIGINT,
            lambda: asyncio.create_task(self.graceful_shutdown()),
        )
        loop.add_signal_handler(
            signal.SIGTERM,
            lambda: asyncio.create_task(self.graceful_shutdown()),
        )

        try:
            # Stage A: Direct calls before workers start
            self._renderer_process = await start_renderer(self.socket_path)
            self._client = SocketClient()
            await self._client.connect(self.socket_path)
            await self._client.send_command(
                "CHANGE AUDIO SOURCE", audio_source=self.audio_source
            )
            await self._client.send_command("INIT")
            self._renderer_ready = True

            # Build dispatch tables from stored keybindings
            self.renderer_dispatch_table = build_renderer_dispatch_table(
                next_preset_key=self._renderer_keybindings.next_preset,
                previous_preset_key=self._renderer_keybindings.previous_preset,
                quit_key=self._renderer_keybindings.quit,
            )

            # Load initial preset
            if not await load_preset_with_retry(self):
                self.post_message(LogMessage("All presets failed to load", level="warning"))

            # Stage B: Start workers
            self.run_worker(stderr_monitor_task(self), name="stderr_monitor")
            self.run_worker(auto_advance_loop(self), name="auto_advance")

            # Stage C: Send final startup commands
            await self._client.send_command("SHOW WINDOW")
            if self.fullscreen:
                await self._client.send_command("SET FULLSCREEN", enabled=True)

        except Exception as e:
            # Clean up on startup failure
            if self._renderer_process is not None:
                self._renderer_process.terminate()
                await self._renderer_process.wait()
            if self._client is not None:
                self._client.close()
            self.exit(message=str(e))

    async def action_quit(self) -> None:
        """Quit the application gracefully.

        Sends QUIT command to renderer and closes connections.
        """
        await self.graceful_shutdown()

    async def action_next_preset(self) -> None:
        """Advance to the next preset in the playlist.

        Silently ignores if renderer not ready, exiting, or at end with
        loop disabled. Posts LogMessage warning on preset load failure.
        """
        if not self._renderer_ready or self._exiting:
            return
        path = self.playlist.next()
        if path is None:
            return
        try:
            await self._client.send_command("LOAD PRESET", path=str(path))
        except RendererError as e:
            self.post_message(LogMessage(f"Failed to load preset: {e}", level="warning"))

    async def action_previous_preset(self) -> None:
        """Go back to the previous preset in the playlist.

        Silently ignores if renderer not ready, exiting, or at start with
        loop disabled. Posts LogMessage warning on preset load failure.
        """
        if not self._renderer_ready or self._exiting:
            return
        path = self.playlist.previous()
        if path is None:
            return
        try:
            await self._client.send_command("LOAD PRESET", path=str(path))
        except RendererError as e:
            self.post_message(LogMessage(f"Failed to load preset: {e}", level="warning"))

    async def graceful_shutdown(self) -> None:
        """Shut down the application gracefully.

        Sets the exiting flag, sends QUIT command to the renderer (if
        reachable), closes the socket, and exits the application.
        """
        self._exiting = True
        try:
            await self._client.send_command("QUIT")
        except ConnectionError:
            pass  # Renderer already gone
        self._client.close()
        self.exit()

    async def on_key(self, event: Key) -> None:
        """Handle terminal key events.

        Dispatches key events to actions via the client dispatch table.

        Args:
            event: The key event from Textual.
        """
        await dispatch_key_event(event.key, self.client_dispatch_table, self)

    def on_log_message(self, message: LogMessage) -> None:
        """Handle log messages by writing to the RichLog widget.

        Args:
            message: The log message to display.
        """
        log_widget = self.query_one("#log", RichLog)
        log_widget.write(message.text)
