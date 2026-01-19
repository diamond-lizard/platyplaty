#!/usr/bin/env python3
"""Autoplay manager for toggle-able autoplay with timer management."""

import asyncio
from contextlib import suppress
from pathlib import Path
from platyplaty.autoplay_helpers import find_next_playable, try_load_preset, show_no_playable_error, show_empty_playlist_error
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
        first_playable = find_next_playable(playlist.presets, -1)
        if first_playable is None:
            self._autoplay_enabled = False
            show_no_playable_error(self._app)
            return
        playlist.set_playing(first_playable)
        playlist.set_selection(first_playable)
        await try_load_preset(self._ctx, playlist.presets[first_playable])
        self._start_timer()

    def _start_timer(self) -> None:
        """Start the autoplay timer task."""
        if self._timer_task is not None:
            self._timer_task.cancel()
        self._timer_task = asyncio.create_task(self._timer_loop())

    def _stop_timer(self) -> None:
        """Stop the autoplay timer task."""
        if self._timer_task is not None:
            self._timer_task.cancel()
            self._timer_task = None

    def _stop_autoplay_with_error(self) -> None:
        """Stop autoplay and show error message for no playable presets."""
        self._autoplay_enabled = False
        self._stop_timer()
        show_no_playable_error(self._app)

    async def _timer_loop(self) -> None:
        """Run the autoplay timer loop."""
        with suppress(asyncio.CancelledError):
            await self._run_autoplay_cycle()

    async def _run_autoplay_cycle(self) -> None:
        """Execute the autoplay cycle until disabled or cancelled."""
        while self._autoplay_enabled and await self._wait_and_advance():
            pass

    async def _wait_and_advance(self) -> bool:
        """Wait for preset_duration then advance. Returns False if cancelled."""
        await asyncio.sleep(self._preset_duration)
        if not self._autoplay_enabled:
            return False
        if not await self.advance_to_next():
            self._stop_autoplay_with_error()
            return False
        return True

    async def advance_to_next(self) -> bool:
        """Advance to the next preset in the playlist.

        Handles looping and skipping of broken presets.

        Returns:
            True if successfully advanced to a playable preset.
        """
        playlist = self._ctx.playlist
        current_index = playlist.get_playing()
        if current_index is None:
            current_index = -1
        next_index = find_next_playable(playlist.presets, current_index)
        if next_index is None:
            return False
        if next_index == current_index:
            return True  # Single-preset playlist, don't reload
        playlist.set_playing(next_index)
        playlist.set_selection(next_index)
        await try_load_preset(self._ctx, playlist.presets[next_index])
        return True
