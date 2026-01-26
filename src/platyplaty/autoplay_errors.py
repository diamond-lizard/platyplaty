#!/usr/bin/env python3
"""Error message display functions for autoplay."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp


NO_PLAYABLE_MESSAGE = "No playable presets in playlist. Stopping autoplay."
EMPTY_PLAYLIST_MESSAGE = "Playlist is empty"


# Error substrings that indicate the renderer connection is dead.
# When these errors occur, don't mark presets as broken - the crash
# handler will mark the actual crashed preset.
_CONNECTION_DEAD_INDICATORS = (
    "Broken pipe",
    "BrokenPipeError",
    "Connection closed",
    "Connection lost",
)


def is_renderer_connection_error(error: str) -> bool:
    """Check if an error indicates the renderer connection is dead.

    Args:
        error: The error message string.

    Returns:
        True if the error indicates a dead connection, False otherwise.
    """
    return any(indicator in error for indicator in _CONNECTION_DEAD_INDICATORS)

def show_no_playable_error(app: "PlatyplatyApp") -> None:
    """Show error message when no playable presets are found.

    Args:
        app: The Textual application instance.
    """
    from platyplaty.ui.command_line import CommandLine
    cmd_line = app.query_one("#command_line", CommandLine)
    cmd_line.show_transient_error(NO_PLAYABLE_MESSAGE)


def show_empty_playlist_error(app: "PlatyplatyApp") -> None:
    """Show error message when playlist is empty.

    Args:
        app: The Textual application instance.
    """
    from platyplaty.ui.command_line import CommandLine
    cmd_line = app.query_one("#command_line", CommandLine)
    cmd_line.show_transient_error(EMPTY_PLAYLIST_MESSAGE)
