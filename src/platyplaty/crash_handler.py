#!/usr/bin/env python3
"""Crash handler for renderer process crashes.

This module contains the logic for handling renderer crashes caused by
problematic presets. When a crash is detected, this handler:

1. Marks the crashed preset as bad (file presets only, not idle://)
2. Updates playlist broken_indices for all matching presets
3. Stops autoplay if running
4. Cleans up renderer state (process, client, renderer_ready)
5. Shows a persistent message instructing the user to load a preset
6. Refreshes the playlist view to show updated broken styling
"""
from pathlib import Path
from typing import TYPE_CHECKING

from platyplaty.bad_presets import mark_preset_as_bad
from platyplaty.playlist_action_helpers import refresh_playlist_view
from platyplaty.playlist_broken import mark_all_matching_as_broken

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext


async def handle_renderer_crash(ctx: "AppContext", app: "PlatyplatyApp") -> None:
    """Handle a renderer crash caused by a problematic preset.

    This function is called when the renderer process dies after a preset
    has been loaded. It performs cleanup and allows the user to continue
    using the app by loading a different preset (which will restart the
    renderer).

    Does NOT set ctx.exiting to True - the app continues running after
    crash handling. The user can load another preset to restart the renderer.

    Args:
        ctx: Application context with renderer state.
        app: The Textual application instance.
    """
    from platyplaty.ui.command_line import CommandLine

    crashed_preset = ctx.preset_sent_to_renderer

    # Mark file presets as bad (skip idle:// which is a str)
    if isinstance(crashed_preset, Path):
        mark_preset_as_bad(crashed_preset)
        mark_all_matching_as_broken(ctx.playlist, crashed_preset)

    # Stop autoplay if running
    if ctx.autoplay_manager is not None and ctx.autoplay_manager.autoplay_enabled:
        ctx.autoplay_manager.stop_autoplay()

    # Clean up renderer state
    ctx.renderer_process = None
    if ctx.client is not None:
        ctx.client.close()
        ctx.client = None
    ctx.renderer_ready = False

    # Show persistent message
    command_line = app.query_one("#command_line", CommandLine)
    message = "Renderer crashed. Load a preset to restart it."
    command_line.show_persistent_message(message)

    # Refresh playlist view to show broken styling
    refresh_playlist_view(app)

    # Refresh file browser to show bad preset styling
    from platyplaty.ui.file_browser import FileBrowser
    file_browser = app.query_one(FileBrowser)
    file_browser.refresh()
