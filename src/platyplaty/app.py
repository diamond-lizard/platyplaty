#!/usr/bin/env python3
"""Textual application for Platyplaty visualizer control."""

from typing import TYPE_CHECKING

from textual.app import App, ComposeResult
from textual.events import Key
from textual.widgets import RichLog, Static

from platyplaty.app_actions import load_preset_by_direction
from platyplaty.app_context import AppContext
from platyplaty.app_shutdown import perform_graceful_shutdown
from platyplaty.app_startup import on_mount_handler
from platyplaty.keybinding_dispatch import dispatch_focused_key_event
from platyplaty.ui import FileBrowser, TransientErrorBar

if TYPE_CHECKING:
    from platyplaty.messages import LogMessage
    from platyplaty.playlist import Playlist
    from platyplaty.types.app_config import AppConfig


class PlatyplatyApp(App[None]):
    """Textual application for controlling the Platyplaty visualizer.

    This app manages the renderer process, handles keyboard input from both
    the terminal and the renderer window, and coordinates auto-advance and
    other background tasks.
    """

    CSS_PATH = "platyplaty.tcss"

    ctx: "AppContext"


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
        # Use ANSI color codes directly instead of Textual's theme-based color
        # conversion. Without this, Textual converts named colors like "blue" to
        # RGB values from its theme palette (e.g., textual-dark), which can map
        # to completely different terminal colors. Setting ansi_color=True makes
        # Textual emit standard ANSI escape codes (e.g., \x1b[34m for blue),
        # allowing the terminal to use its configured color palette. This must
        # be set after super().__init__() to properly trigger Textual's reactive
        # attribute system.
        self.ansi_color = True

        # Create AppContext which builds dispatch tables in __post_init__
        self.ctx = AppContext(config=config, playlist=playlist)

    def compose(self) -> ComposeResult:
        """Create child widgets for the application.

        Returns:
            Widgets to mount in the application.
        """
        yield Static("Platyplaty Visualizer", id="status")
        yield FileBrowser(self.ctx.file_browser_dispatch_table, id="file_browser")
        yield RichLog(id="log")
        yield TransientErrorBar(id="transient_error")


    async def on_mount(self) -> None:
        """Perform startup sequence when the app is mounted."""
        await on_mount_handler(self.ctx, self)

    async def action_quit(self) -> None:
        """Quit the application gracefully."""
        await self.graceful_shutdown()

    async def action_next_preset(self) -> None:
        """Advance to the next preset in the playlist."""
        await load_preset_by_direction(self.ctx, self, self.ctx.playlist.next, "next")

    async def action_previous_preset(self) -> None:
        """Go back to the previous preset in the playlist."""
        await load_preset_by_direction(
            self.ctx, self, self.ctx.playlist.previous, "previous"
        )

    async def action_navigate_up(self) -> None:
        """Move selection up in current focused section."""
        from platyplaty.app_playlist_actions import action_navigate_up

        await action_navigate_up(self)

    async def action_navigate_down(self) -> None:
        """Move selection down in current focused section."""
        from platyplaty.app_playlist_actions import action_navigate_down

        await action_navigate_down(self)

    async def action_play_next(self) -> None:
        """Play next preset in playlist."""
        from platyplaty.app_playlist_actions import action_play_next

        await action_play_next(self)

    async def action_play_previous(self) -> None:
        """Play previous preset in playlist."""
        from platyplaty.app_playlist_actions import action_play_previous

        await action_play_previous(self)

    async def action_reorder_up(self) -> None:
        """Move selected preset up in playlist."""
        from platyplaty.app_playlist_actions import action_reorder_up

        await action_reorder_up(self)

    async def action_reorder_down(self) -> None:
        """Move selected preset down in playlist."""
        from platyplaty.app_playlist_actions import action_reorder_down

        await action_reorder_down(self)

    async def action_delete_from_playlist(self) -> None:
        """Delete selected preset from playlist."""
        from platyplaty.app_playlist_actions import action_delete_from_playlist

        await action_delete_from_playlist(self)

    async def action_undo(self) -> None:
        """Undo the last playlist operation."""
        from platyplaty.app_playlist_actions import action_undo

        await action_undo(self)

    async def action_redo(self) -> None:
        """Redo the last undone playlist operation."""
        from platyplaty.app_playlist_actions import action_redo

        await action_redo(self)

    async def action_play_selection(self) -> None:
        """Play the currently selected preset."""
        from platyplaty.app_playlist_actions import action_play_selection

        if self.ctx.current_focus == "playlist":
            await action_play_selection(self)

    async def action_open_selected(self) -> None:
        """Open selected item - enters directory or opens in editor."""
        if self.ctx.current_focus == "playlist":
            from platyplaty.app_playlist_actions import action_open_selected

            await action_open_selected(self)

    async def action_page_up(self) -> None:
        """Move selection up by one page."""
        from platyplaty.app_playlist_actions import action_page_up

        await action_page_up(self)

    async def action_page_down(self) -> None:
        """Move selection down by one page."""
        from platyplaty.app_playlist_actions import action_page_down

        await action_page_down(self)

    async def action_navigate_to_first_preset(self) -> None:
        """Move selection to first preset."""
        from platyplaty.app_playlist_actions import action_navigate_to_first_preset

        await action_navigate_to_first_preset(self)

    async def action_navigate_to_last_preset(self) -> None:
        """Move selection to last preset."""
        from platyplaty.app_playlist_actions import action_navigate_to_last_preset

        await action_navigate_to_last_preset(self)

    async def action_shuffle_playlist(self) -> None:
        """Shuffle the playlist in place."""
        from platyplaty.app_playlist_actions import action_shuffle_playlist

        await action_shuffle_playlist(self)

    async def graceful_shutdown(self) -> None:
        """Shut down the application gracefully."""
        await perform_graceful_shutdown(self.ctx, self)

    async def on_key(self, event: Key) -> None:
        """Handle terminal key events."""
        await dispatch_focused_key_event(event.key, self.ctx, self)

    def on_log_message(self, message: "LogMessage") -> None:
        """Handle log messages by writing to the RichLog widget."""
        self.query_one("#log", RichLog).write(message.text)
