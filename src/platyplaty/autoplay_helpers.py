#!/usr/bin/env python3
"""Helper functions for autoplay preset validation and loading."""

from pathlib import Path
from typing import TYPE_CHECKING

from platyplaty.socket_exceptions import RendererError

if TYPE_CHECKING:
    from platyplaty.app_context import AppContext
    from platyplaty.app import PlatyplatyApp


def is_preset_playable(path: Path) -> bool:
    """Check if a preset file is playable.

    Args:
        path: Path to the preset file.

    Returns:
        True if the file exists, is readable, and is not a broken symlink.
    """
    try:
        if path.is_symlink() and not path.exists():
            return False
        return path.is_file() and path.exists()
    except OSError:
        return False


async def try_load_preset(ctx: "AppContext", path: Path) -> bool:
    """Attempt to load a preset into the renderer.

    Args:
        ctx: Application context with client.
        path: Path to the preset file.

    Returns:
        True if loaded successfully, False otherwise.
    """
    if not ctx.client:
        return False
    try:
        await ctx.client.send_command("LOAD PRESET", path=str(path))
        return True
    except RendererError:
        return False


def find_next_playable(presets: list[Path], start_index: int) -> int | None:
    """Find the next playable preset starting from start_index.
    
    Iterates through the playlist starting from start_index + 1,
    wrapping to the beginning and stopping before reaching start_index again.
    
    Args:
        presets: List of preset paths.
        start_index: Index to start searching from (not included).
    
    Returns:
        Index of the next playable preset, or None if no playable preset found.
    """
    if not presets:
        return None
    count = len(presets)
    for offset in range(1, count + 1):
        index = (start_index + offset) % count
        if is_preset_playable(presets[index]):
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
