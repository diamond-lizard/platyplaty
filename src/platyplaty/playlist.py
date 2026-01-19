#!/usr/bin/env python3
"""Playlist class for managing presets with navigation and state."""

from pathlib import Path

from platyplaty import playlist_navigation as nav
from platyplaty import playlist_operations as ops
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
        ops.add_preset(self.presets, path)
        self.dirty_flag = True
        self._validate_new_preset(path)

    def remove_preset(self, index: int) -> None:
        """Remove the preset at the given index."""
        ops.remove_preset(self.presets, index)
        self.dirty_flag = True
        self._adjust_broken_indices_after_remove(index)

    def move_preset_up(self, index: int) -> bool:
        """Move preset at index up by one. Return False if at top."""
        result = ops.move_preset_up(self.presets, index)
        self.dirty_flag = self.dirty_flag or result
        if result:
            self._swap_broken_indices(index - 1, index)
        return result

    def move_preset_down(self, index: int) -> bool:
        """Move preset at index down by one. Return False if at bottom."""
        result = ops.move_preset_down(self.presets, index)
        self.dirty_flag = self.dirty_flag or result
        if result:
            self._swap_broken_indices(index, index + 1)
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

    def _validate_new_preset(self, path: Path) -> None:
        """Check if newly added preset is broken and update broken_indices."""
        from platyplaty.preset_validator import is_valid_preset

        new_index = len(self.presets) - 1
        if not is_valid_preset(path):
            self.broken_indices.add(new_index)

    def _adjust_broken_indices_after_remove(self, removed_index: int) -> None:
        """Adjust broken_indices after a preset is removed."""
        self.broken_indices.discard(removed_index)
        self.broken_indices = {
            i - 1 if i > removed_index else i for i in self.broken_indices
        }

    def _swap_broken_indices(self, idx1: int, idx2: int) -> None:
        """Swap positions in broken_indices when presets are swapped."""
        has_idx1 = idx1 in self.broken_indices
        has_idx2 = idx2 in self.broken_indices
        if has_idx1 != has_idx2:
            if has_idx1:
                self.broken_indices.discard(idx1)
                self.broken_indices.add(idx2)
            else:
                self.broken_indices.discard(idx2)
                self.broken_indices.add(idx1)
