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
        from platyplaty.playlist_nav_actions import navigate_up

        await navigate_up(self.ctx, self)

    async def action_navigate_down(self) -> None:
        """Move selection down in current focused section."""
        from platyplaty.playlist_nav_actions import navigate_down

        await navigate_down(self.ctx, self)

    async def action_play_next(self) -> None:
        """Play next preset in playlist."""
        from platyplaty.playlist_play_actions import play_next

        await play_next(self.ctx, self)

    async def action_play_previous(self) -> None:
        """Play previous preset in playlist."""
        from platyplaty.playlist_play_actions import play_previous

        await play_previous(self.ctx, self)

    async def action_reorder_up(self) -> None:
        """Move selected preset up in playlist."""
        from platyplaty.playlist_edit_actions import reorder_up

        await reorder_up(self.ctx, self)

    async def action_reorder_down(self) -> None:
        """Move selected preset down in playlist."""
        from platyplaty.playlist_edit_actions import reorder_down

        await reorder_down(self.ctx, self)

    async def action_delete_from_playlist(self) -> None:
        """Delete selected preset from playlist."""
        from platyplaty.playlist_delete_action import delete_from_playlist

        await delete_from_playlist(self.ctx, self)

    async def action_undo(self) -> None:
        """Undo the last playlist operation."""
        from platyplaty.playlist_undo_actions import undo

        await undo(self.ctx, self)

    async def action_redo(self) -> None:
        """Redo the last undone playlist operation."""
        from platyplaty.playlist_undo_actions import redo

        await redo(self.ctx, self)

    async def action_play_selection(self) -> None:
        """Play the currently selected preset."""
        from platyplaty.playlist_play_actions import play_selection

        if self.ctx.current_focus == "playlist":
            await play_selection(self.ctx, self)

    async def action_open_selected(self) -> None:
        """Open selected item - enters directory or opens in editor."""
        if self.ctx.current_focus == "playlist":
            from platyplaty.playlist_play_actions import open_selected

            await open_selected(self.ctx, self)

    async def action_page_up(self) -> None:
        """Move selection up by one page."""
        from platyplaty.playlist_page_actions import page_up

        await page_up(self.ctx, self)

    async def action_page_down(self) -> None:
        """Move selection down by one page."""
        from platyplaty.playlist_page_actions import page_down

        await page_down(self.ctx, self)

    async def action_navigate_to_first_preset(self) -> None:
        """Move selection to first preset."""
        from platyplaty.playlist_jump_actions import navigate_to_first_preset

        await navigate_to_first_preset(self.ctx, self)

    async def action_navigate_to_last_preset(self) -> None:
        """Move selection to last preset."""
        from platyplaty.playlist_jump_actions import navigate_to_last_preset

        await navigate_to_last_preset(self.ctx, self)

    async def action_shuffle_playlist(self) -> None:
        """Shuffle the playlist in place."""
        from platyplaty.playlist_edit_actions import shuffle_playlist

        await shuffle_playlist(self.ctx, self)

    async def action_save_playlist(self) -> None:
        """Save the playlist to its associated filename."""
        from platyplaty.playlist_edit_actions import save_playlist

        await save_playlist(self.ctx, self)

    async def action_toggle_autoplay(self) -> None:
        """Toggle autoplay on or off."""
        from platyplaty.playlist_play_actions import toggle_autoplay

        await toggle_autoplay(self.ctx, self)

    async def graceful_shutdown(self) -> None:
        """Shut down the application gracefully."""
        await perform_graceful_shutdown(self.ctx, self)

    async def on_key(self, event: Key) -> None:
        """Handle terminal key events."""
        await dispatch_focused_key_event(event.key, self.ctx, self)

    def on_log_message(self, message: "LogMessage") -> None:
        """Handle log messages by writing to the RichLog widget."""
        self.query_one("#log", RichLog).write(message.text)
