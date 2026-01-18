#!/usr/bin/env python3
"""Playlist persistence operations.

Functions for loading, saving, and clearing playlist state.
"""

from pathlib import Path
from typing import TYPE_CHECKING

from platyplaty.playlist_file import parse_playlist_file, write_playlist_file

if TYPE_CHECKING:
    from platyplaty.playlist import Playlist


def clear_playlist(playlist: "Playlist") -> None:
    """Remove all presets and clear associated filename."""
    playlist.presets.clear()
    playlist.associated_filename = None
    playlist._selection_index = 0
    playlist._playing_index = None
    playlist.dirty_flag = True


def load_from_file(playlist: "Playlist", filepath: Path) -> None:
    """Load presets from a .platy file, replacing current contents."""
    playlist.presets = parse_playlist_file(filepath)
    playlist.associated_filename = filepath
    playlist._selection_index = 0
    playlist._playing_index = 0 if playlist.presets else None
    playlist.dirty_flag = False


def save_to_file(playlist: "Playlist", filepath: Path | None = None) -> None:
    """Save presets to a .platy file."""
    if filepath is None:
        filepath = playlist.associated_filename
    if filepath is None:
        raise ValueError("No file name")
    write_playlist_file(filepath, playlist.presets)
    playlist.associated_filename = filepath
    playlist.dirty_flag = False
