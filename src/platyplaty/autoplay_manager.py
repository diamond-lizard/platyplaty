#!/usr/bin/env python3
"""Autoplay manager for toggle-able autoplay with timer management."""

import asyncio
from platyplaty.autoplay_helpers import find_next_playable, try_load_preset, show_no_playable_error, show_empty_playlist_error
from platyplaty.autoplay_timer import run_timer_loop
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app_context import AppContext
    from platyplaty.app import PlatyplatyApp


class AutoplayManager:
    """Manages toggle-able autoplay with timer-based advancement."""

    def __init__(
        self, ctx: "AppContext", app: "PlatyplatyApp", preset_duration: float
    ) -> None:
        """Initialize the autoplay manager.

        Args:
            ctx: Application context with playlist and client.
            app: The Textual application for posting messages.
            preset_duration: Seconds between preset changes.
        """
        self._ctx = ctx
        self._app = app
        self._preset_duration = preset_duration
        self._autoplay_enabled = False
        self._timer_task: asyncio.Task[None] | None = None

    @property
    def autoplay_enabled(self) -> bool:
        """Return whether autoplay is currently enabled."""
        return self._autoplay_enabled

    @property
    def preset_duration(self) -> float:
        """Return the preset duration in seconds."""
        return self._preset_duration

    async def toggle_autoplay(self) -> bool:
        """Toggle autoplay on or off.
        
        Returns:
            True if autoplay is now enabled, False if disabled.
        """
        if self._autoplay_enabled:
            self._stop_timer()
            self._autoplay_enabled = False
        else:
            self._autoplay_enabled = True
            await self._start_autoplay()
        return self._autoplay_enabled

    async def _start_autoplay(self) -> None:
        """Start autoplay, loading first preset if idle."""
        playlist = self._ctx.playlist
        playing = playlist.get_playing()
        if playing is not None:
            playlist.set_selection(playing)
            self._start_timer()
            return
        if not playlist.presets:
            self._autoplay_enabled = False
            show_empty_playlist_error(self._app)
            return
        first_playable = find_next_playable(playlist, -1)
        if first_playable is None:
            self._autoplay_enabled = False
            show_no_playable_error(self._app)
            return
        playlist.set_playing(first_playable)
        playlist.set_selection(first_playable)
        success, error = await try_load_preset(self._ctx, playlist.presets[first_playable])
        if not success and error is not None:
            playlist.broken_indices.add(first_playable)
            self._ctx.error_log.append(error)
            from platyplaty.autoplay_advance import advance_playlist_to_next
            if not await advance_playlist_to_next(self._ctx, playlist):
                self._autoplay_enabled = False
                show_no_playable_error(self._app)
                return
        self._start_timer()

    def _start_timer(self) -> None:
        """Start the autoplay timer task."""
        if self._timer_task is not None:
            self._timer_task.cancel()
        self._timer_task = asyncio.create_task(run_timer_loop(self))

    def _stop_timer(self) -> None:
        """Stop the autoplay timer task."""
        if self._timer_task is not None:
            self._timer_task.cancel()
            self._timer_task = None

    def stop_autoplay_with_error(self) -> None:
        """Stop autoplay and show error message for no playable presets."""
        self._autoplay_enabled = False
        self._stop_timer()
        show_no_playable_error(self._app)

    async def advance_to_next(self) -> bool:
        """Advance to the next preset in the playlist."""
        from platyplaty.autoplay_advance import advance_playlist_to_next
        return await advance_playlist_to_next(self._ctx, self._ctx.playlist)
