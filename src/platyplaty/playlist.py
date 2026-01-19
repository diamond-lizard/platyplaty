#!/usr/bin/env python3
"""Playlist class for managing presets with navigation and state."""

from pathlib import Path

from platyplaty import playlist_modify as modify
from platyplaty import playlist_navigation as nav
from platyplaty import playlist_persistence as persist


class Playlist:
    """Manages a list of presets with navigation and state tracking."""

    presets: list[Path]
    loop: bool
    _playing_index: int | None
    _selection_index: int
    associated_filename: Path | None
    dirty_flag: bool
    broken_indices: set[int]

    def __init__(self, presets: list[Path], loop: bool = True) -> None:
        """Initialize playlist with presets and optional loop setting."""
        self.presets = presets
        self.loop = loop
        self._playing_index = 0
        self._selection_index = 0
        self.associated_filename = None
        self.dirty_flag = False
        self.broken_indices: set[int] = set()

    def current(self) -> Path:
        """Return the current preset path."""
        return nav.get_current(self.presets, self._playing_index)

    def at_end(self) -> bool:
        """Return True if at the last preset."""
        return nav.is_at_end(self.presets, self._playing_index)

    def next(self) -> Path | None:
        """Advance to the next preset."""
        result = nav.advance_next(self.presets, self._playing_index, self.loop)
        if result is None:
            return None
        self._playing_index, preset = result
        return preset

    def previous(self) -> Path | None:
        """Move to the previous preset."""
        result = nav.go_previous(self.presets, self._playing_index, self.loop)
        if result is None:
            return None
        self._playing_index, preset = result
        return preset

    def get_selection(self) -> int:
        """Return the current selection index."""
        return self._selection_index

    def set_selection(self, index: int) -> None:
        """Set the selection index."""
        self._selection_index = index

    def get_playing(self) -> int | None:
        """Return the current playing index, or None if idle."""
        return self._playing_index

    def set_playing(self, index: int | None) -> None:
        """Set the playing index. None means idle preset."""
        self._playing_index = index

    def add_preset(self, path: Path) -> None:
        """Add a preset at the end of the playlist."""
        modify.add_preset_to_playlist(self.presets, self.broken_indices, path)
        self.dirty_flag = True

    def remove_preset(self, index: int) -> None:
        """Remove the preset at the given index."""
        self.broken_indices = modify.remove_preset_from_playlist(
            self.presets, self.broken_indices, index
        )
        self.dirty_flag = True

    def move_preset_up(self, index: int) -> bool:
        """Move preset at index up by one. Return False if at top."""
        result = modify.move_preset_up_in_playlist(
            self.presets, self.broken_indices, index
        )
        self.dirty_flag = self.dirty_flag or result
        return result

    def move_preset_down(self, index: int) -> bool:
        """Move preset at index down by one. Return False if at bottom."""
        result = modify.move_preset_down_in_playlist(
            self.presets, self.broken_indices, index
        )
        self.dirty_flag = self.dirty_flag or result
        return result

    def clear(self) -> None:
        """Remove all presets and clear associated filename."""
        persist.clear_playlist(self)

    def load_from_file(self, filepath: Path) -> None:
        """Load presets from a .platy file, replacing current contents."""
        persist.load_from_file(self, filepath)

    def save_to_file(self, filepath: Path | None = None) -> None:
        """Save presets to a .platy file."""
        persist.save_to_file(self, filepath)
