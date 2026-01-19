#!/usr/bin/env python3
"""Helper functions for creating and restoring playlist snapshots."""

from typing import TYPE_CHECKING

from platyplaty.undo import PlaylistSnapshot

if TYPE_CHECKING:
    from platyplaty.playlist import Playlist


def create_snapshot(playlist: "Playlist") -> PlaylistSnapshot:
    """Create an immutable snapshot of the playlist's current state.

    Captures all state needed to restore the playlist:
    - presets list (as tuple for immutability)
    - selection index
    - playing index
    - associated filename
    - dirty flag

    Args:
        playlist: The playlist to snapshot.

    Returns:
        An immutable PlaylistSnapshot.
    """
    return PlaylistSnapshot(
        presets=tuple(playlist.presets),
        selection_index=playlist.get_selection(),
        playing_index=playlist.get_playing(),
        associated_filename=playlist.associated_filename,
        dirty_flag=playlist.dirty_flag,
    )


def restore_snapshot(playlist: "Playlist", snapshot: PlaylistSnapshot) -> None:
    """Restore a playlist to a previous state from a snapshot.

    Restores all state from the snapshot:
    - presets list
    - selection index
    - playing index
    - associated filename
    - dirty flag

    Args:
        playlist: The playlist to restore.
        snapshot: The snapshot containing state to restore.
    """
    playlist.presets = list(snapshot.presets)
    playlist.set_selection(snapshot.selection_index)
    playlist.set_playing(snapshot.playing_index)
    playlist.associated_filename = snapshot.associated_filename
    playlist.dirty_flag = snapshot.dirty_flag
