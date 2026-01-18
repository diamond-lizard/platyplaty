#!/usr/bin/env python3
"""Keybinding configuration container for Platyplaty."""

from pydantic import BaseModel, ConfigDict, Field

from platyplaty.types.keybindings_error_view import ErrorViewKeybindings
from platyplaty.types.keybindings_file_browser import FileBrowserKeybindings
from platyplaty.types.keybindings_global import GlobalKeybindings
from platyplaty.types.keybindings_playlist import PlaylistKeybindings


class Keybindings(BaseModel):
    """Container for all keybinding sections.

    Attributes:
        globals: Keybindings available in all sections.
        file_browser: Keybindings for file browser section.
        playlist: Keybindings for playlist section.
        error_view: Keybindings for error view section.
    """

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    globals: GlobalKeybindings = Field(
        default_factory=GlobalKeybindings, alias="global"
    )
    file_browser: FileBrowserKeybindings = Field(
        default_factory=FileBrowserKeybindings, alias="file-browser"
    )
    playlist: PlaylistKeybindings = Field(default_factory=PlaylistKeybindings)
    error_view: ErrorViewKeybindings = Field(
        default_factory=ErrorViewKeybindings, alias="error-view"
    )
