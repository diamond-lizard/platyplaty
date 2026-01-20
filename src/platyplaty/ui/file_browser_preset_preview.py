"""Preset preview action for the file browser.

This module provides the ENTER key action for previewing presets
by loading them into the renderer without adding them to the playlist.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from platyplaty.ui.directory_types import EntryType
from platyplaty.ui.file_browser_error import show_transient_error

if TYPE_CHECKING:
    from platyplaty.ui.file_browser import FileBrowser


async def action_preview_preset(browser: FileBrowser) -> None:
    """Preview selected preset by loading into renderer.

    For .milk files or symlinks to .milk files, loads into renderer.
    For other entry types (directories, .platy files, broken symlinks),
    this is a no-op.

    Args:
        browser: The file browser instance.
    """
    entry = browser.get_selected_entry()
    if entry is None:
        return
    suffix = entry.path.suffix.lower()
    is_milk = suffix == ".milk"
    is_file = entry.entry_type in (EntryType.FILE, EntryType.SYMLINK_TO_FILE)
    if not (is_milk and is_file):
        return
    await _preview_milk_preset(browser, entry.path)


async def _preview_milk_preset(browser: FileBrowser, path) -> None:
    """Load a preset into the renderer for preview.

    Args:
        browser: The file browser instance.
        path: Path to the preset file.
    """
    from platyplaty.autoplay_helpers import try_load_preset

    ctx = browser.platyplaty_app.ctx
    _stop_autoplay_if_running(ctx)
    success, error = await try_load_preset(ctx, path)
    if not success and error:
        show_transient_error(browser, error)
    if success:
        _update_playing_indicator(browser, path)

def _stop_autoplay_if_running(ctx) -> None:
    """Stop autoplay if it is currently running."""
    autoplay_mgr = getattr(ctx, "autoplay_manager", None)
    if autoplay_mgr is not None:
        autoplay_mgr.stop_autoplay()

def _update_playing_indicator(browser: FileBrowser, path) -> None:
    """Update playing indicator when previewing a preset.

    If preset is in playlist, move '* ' indicator to it.
    If not in playlist, remove '* ' indicator.

    Args:
        browser: The file browser instance.
        path: Path to the previewed preset.
    """
    from platyplaty.playlist_action_helpers import (
        find_preset_index,
        refresh_playlist_view,
        scroll_playlist_to_playing,
    )

    ctx = browser.platyplaty_app.ctx
    playlist = ctx.playlist
    index = find_preset_index(playlist, path)
    playlist.set_playing(index)
    refresh_playlist_view(browser.platyplaty_app)
    if index is not None:
        scroll_playlist_to_playing(browser.platyplaty_app)

