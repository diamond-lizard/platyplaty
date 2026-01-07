#!/usr/bin/env python3
"""Playlist module for Platyplaty.

Handles playlist navigation.
"""

from pathlib import Path


class Playlist:
    """Manages a list of presets with navigation.

    Attributes:
        presets: List of preset paths.
        loop: Whether to wrap around at the end.
    """

    presets: list[Path]
    loop: bool
    _index: int

    def __init__(self, presets: list[Path], loop: bool = True) -> None:
        """Initialize the playlist.

        Args:
            presets: List of preset paths.
            loop: Whether to wrap around when reaching the end.
        """
        self.presets = presets
        self.loop = loop
        self._index = 0

    def current(self) -> Path:
        """Return the current preset path."""
        return self.presets[self._index]

    def at_end(self) -> bool:
        """Return True if at the last preset."""
        return self._index >= len(self.presets) - 1

    def next(self) -> Path | None:
        """Advance to the next preset.

        Returns:
            The next preset path, or None if at end and loop is False.
        """
        if self.at_end() and not self.loop:
            return None
        if self.at_end():
            self._index = 0
        else:
            self._index += 1
        return self.presets[self._index]

    def previous(self) -> Path | None:
        """Move to the previous preset.

        Returns:
            The previous preset path, or None if at start and loop is False.
        """
        if self._index == 0 and not self.loop:
            return None
        if self._index == 0:
            self._index = len(self.presets) - 1
        else:
            self._index -= 1
        return self.presets[self._index]
