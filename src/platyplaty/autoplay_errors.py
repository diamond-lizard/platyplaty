#!/usr/bin/env python3
"""Error message display functions for autoplay."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp


NO_PLAYABLE_MESSAGE = "No playable presets in playlist. Stopping autoplay."
EMPTY_PLAYLIST_MESSAGE = "Playlist is empty"


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
