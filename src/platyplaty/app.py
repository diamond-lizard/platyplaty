#!/usr/bin/env python3
"""Textual application for Platyplaty visualizer control."""

from textual.app import App

from platyplaty.messages import LogMessage
from platyplaty.socket_client import RendererError


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

    renderer_dispatch_table: dict[str, str]
    client_dispatch_table: dict[str, str]
    _renderer_ready: bool

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
            await self._client.send_command("LOAD PRESET", {"path": str(path)})
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
            await self._client.send_command("LOAD PRESET", {"path": str(path)})
        except RendererError as e:
            self.post_message(LogMessage(f"Failed to load preset: {e}", level="warning"))
