#!/usr/bin/env python3
"""Playlist module for Platyplaty.

Handles playlist navigation.
"""

from pathlib import Path

from platyplaty.playlist_file import parse_playlist_file, write_playlist_file


class Playlist:
    """Manages a list of presets with navigation.

    Attributes:
        presets: List of preset paths.
        loop: Whether to wrap around at the end.
    """

    presets: list[Path]
    loop: bool
    _playing_index: int | None
    _selection_index: int
    associated_filename: Path | None
    dirty_flag: bool

    def __init__(self, presets: list[Path], loop: bool = True) -> None:
        """Initialize the playlist.

        Args:
            presets: List of preset paths.
            loop: Whether to wrap around when reaching the end.
        """
        self.presets = presets
        self.loop = loop
        self._playing_index = 0
        self._selection_index = 0
        self.associated_filename = None
        self.dirty_flag = False

    def current(self) -> Path:
        """Return the current preset path."""
        return self.presets[self._playing_index]

    def at_end(self) -> bool:
        """Return True if at the last preset."""
        return self._playing_index >= len(self.presets) - 1

    def next(self) -> Path | None:
        """Advance to the next preset.

        Returns:
            The next preset path, or None if at end and loop is False.
        """
        if self.at_end() and not self.loop:
            return None
        if self.at_end():
            self._playing_index = 0
        else:
            self._playing_index += 1
        return self.presets[self._playing_index]

    def previous(self) -> Path | None:
        """Move to the previous preset.

        Returns:
            The previous preset path, or None if at start and loop is False.
        """
        if self._playing_index == 0 and not self.loop:
            return None
        if self._playing_index == 0:
            self._playing_index = len(self.presets) - 1
        else:
            self._playing_index -= 1
        return self.presets[self._playing_index]

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
        self.presets.append(path)
        self.dirty_flag = True

    def remove_preset(self, index: int) -> None:
        """Remove the preset at the given index."""
        del self.presets[index]
        self.dirty_flag = True

    def move_preset_up(self, index: int) -> bool:
        """Move preset at index up by one. Return False if at top."""
        if index <= 0:
            return False
        self.presets[index], self.presets[index - 1] = self.presets[index - 1], self.presets[index]
        self.dirty_flag = True
        return True

    def move_preset_down(self, index: int) -> bool:
        """Move preset at index down by one. Return False if at bottom."""
        if index >= len(self.presets) - 1:
            return False
        self.presets[index], self.presets[index + 1] = self.presets[index + 1], self.presets[index]
        self.dirty_flag = True
        return True

    def clear(self) -> None:
        """Remove all presets and clear associated filename."""
        self.presets.clear()
        self.associated_filename = None
        self._selection_index = 0
        self._playing_index = None
        self.dirty_flag = True

    def load_from_file(self, filepath: Path) -> None:
        """Load presets from a .platy file, replacing current contents."""
        self.presets = parse_playlist_file(filepath)
        self.associated_filename = filepath
        self._selection_index = 0
        self._playing_index = 0 if self.presets else None
        self.dirty_flag = False

    def save_to_file(self, filepath: Path | None = None) -> None:
        """Save presets to a .platy file."""
        if filepath is None:
            filepath = self.associated_filename
        if filepath is None:
            raise ValueError("No file name")
        write_playlist_file(filepath, self.presets)
        self.associated_filename = filepath
        self.dirty_flag = False
