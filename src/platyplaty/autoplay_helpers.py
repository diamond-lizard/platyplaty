#!/usr/bin/env python3
"""Helper functions for autoplay preset validation and loading."""

from pathlib import Path
from typing import TYPE_CHECKING

from platyplaty.socket_exceptions import RendererError

if TYPE_CHECKING:
    from platyplaty.app_context import AppContext
    from platyplaty.app import PlatyplatyApp
    from platyplaty.playlist import Playlist


def is_preset_playable(path: Path) -> bool:
    """Check if a preset file is playable.

    Args:
        path: Path to the preset file.

    Returns:
        True if the file exists, is readable, and is not a broken symlink.
    """
    from platyplaty.preset_validator import is_valid_preset
    return is_valid_preset(path)



def validate_and_mark_broken(playlist: "Playlist", index: int) -> bool:
    """Re-validate preset at index and update broken_indices if needed.

    Args:
        playlist: The playlist containing the preset.
        index: Index of the preset to validate.

    Returns:
        True if preset is valid, False if broken.
    """
    if index < 0 or index >= len(playlist.presets):
        return False
    path = playlist.presets[index]
    if is_preset_playable(path):
        return True
    playlist.broken_indices.add(index)
    return False

async def try_load_preset(ctx: "AppContext", path: Path) -> tuple[bool, str | None]:
    """Attempt to load a preset into the renderer.

    Args:
        ctx: Application context with client.
        path: Path to the preset file.

    Returns:
        Tuple of (success, error_message). error_message is None on success
        or validation failure, contains renderer error message on render error.
    """
    if not ctx.client:
        return (False, None)
    if not is_preset_playable(path):
        return (False, None)
    try:
        await ctx.client.send_command("LOAD PRESET", path=str(path))
        return (True, None)
    except RendererError as e:
        return (False, str(e))


def find_next_playable(playlist: "Playlist", start_index: int) -> int | None:
    """Find the next playable preset starting from start_index.

    Iterates through the playlist starting from start_index + 1,
    wrapping to the beginning and stopping before reaching start_index again.
    Marks any broken presets in playlist.broken_indices.

    Args:
        playlist: The playlist to search.
        start_index: Index to start searching from (not included).

    Returns:
        Index of the next playable preset, or None if no playable preset found.
    """
    presets = playlist.presets
    if not presets:
        return None
    count = len(presets)
    for offset in range(1, count + 1):
        index = (start_index + offset) % count
        if validate_and_mark_broken(playlist, index):
            return index
    return None


NO_PLAYABLE_MESSAGE = "No playable presets in playlist. Stopping autoplay."
EMPTY_PLAYLIST_MESSAGE = "Playlist is empty"


def show_no_playable_error(app: "PlatyplatyApp") -> None:
    """Show error message when no playable presets are found.
    
    Args:
        app: The Textual application instance.
    """
    from platyplaty.ui.transient_error import TransientErrorBar
    error_bar = app.query_one("#transient_error", TransientErrorBar)
    error_bar.show_error(NO_PLAYABLE_MESSAGE)


def show_empty_playlist_error(app: "PlatyplatyApp") -> None:
    """Show error message when playlist is empty.
    
    Args:
        app: The Textual application instance.
    """
    from platyplaty.ui.transient_error import TransientErrorBar
    error_bar = app.query_one("#transient_error", TransientErrorBar)
    error_bar.show_error(EMPTY_PLAYLIST_MESSAGE)
