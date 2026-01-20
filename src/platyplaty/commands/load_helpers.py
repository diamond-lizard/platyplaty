#!/usr/bin/env python3
"""Helper functions for the load playlist command."""

import os
from pathlib import Path
from typing import TYPE_CHECKING

from platyplaty.commands.load_validation import validate_playlist_path
from platyplaty.playlist_file import parse_playlist_file
from platyplaty.playlist_snapshot import push_undo_snapshot

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext


def expand_command_path(path_arg: str, base_dir: Path) -> Path:
    """Expand tilde, environment variables, and resolve relative paths.

    Args:
        path_arg: The path string from the command argument.
        base_dir: Base directory for resolving relative paths.

    Returns:
        Fully expanded and resolved Path.
    """
    expanded = os.path.expandvars(os.path.expanduser(path_arg))
    result = Path(expanded)
    if not result.is_absolute():
        result = base_dir / result
    return result


async def load_and_play_playlist(
    path_arg: str, ctx: "AppContext", app: "PlatyplatyApp", base_dir: Path
) -> tuple[bool, str | None]:
    """Load a playlist file and start playing.

    Args:
        path_arg: Path argument from the command.
        ctx: Application context.
        app: The Textual application.
        base_dir: Base directory for resolving relative paths.

    Returns:
        Tuple of (success, error_message). error_message is None on success.
    """
    filepath = expand_command_path(path_arg, base_dir)
    error = validate_playlist_path(filepath)
    if error:
        return (False, error)
    push_undo_snapshot(ctx)
    return await perform_load(filepath, ctx, app)




async def perform_load(
    filepath: Path, ctx: "AppContext", app: "PlatyplatyApp"
) -> tuple[bool, str | None]:
    """Perform the actual playlist load and start playing.

    Args:
        filepath: Path to the playlist file.
        ctx: Application context.
        app: The Textual application.

    Returns:
        Tuple of (success, error_message).
    """
    try:
        presets = parse_playlist_file(filepath)
    except Exception as e:
        return (False, f"Error: could not load playlist: {e}")
    ctx.playlist.presets = presets
    ctx.playlist.associated_filename = filepath
    ctx.playlist.dirty_flag = False
    ctx.playlist._selection_index = 0
    ctx.playlist.broken_indices = set()
    await start_playing_after_load(ctx, app)
    return (True, None)


async def start_playing_after_load(ctx: "AppContext", app: "PlatyplatyApp") -> None:
    """Start playing after a playlist load.

    Handles empty playlist (idle), non-empty playlist (first preset),
    and autoplay continuation.

    Args:
        ctx: Application context.
        app: The Textual application.
    """
    from platyplaty.commands.load_play import play_after_load
    await play_after_load(ctx, app)
