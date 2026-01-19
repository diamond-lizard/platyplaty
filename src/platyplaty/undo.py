#!/usr/bin/env python3
"""Undo/redo system for playlist modifications."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class PlaylistSnapshot:
    """Immutable snapshot of playlist state for undo/redo."""

    presets: tuple[Path, ...]
    selection_index: int
    playing_index: int | None
    associated_filename: Path | None
    dirty_flag: bool


class UndoManager:
    """Manages undo/redo stacks for playlist state."""

    MAX_UNDO_LEVELS = 1000

    def __init__(self) -> None:
        """Initialize empty undo and redo stacks."""
        self._undo_stack: list[PlaylistSnapshot] = []
        self._redo_stack: list[PlaylistSnapshot] = []

    def push_undo(self, snapshot: PlaylistSnapshot) -> None:
        """Save state before a modification."""
        self._undo_stack.append(snapshot)
        if len(self._undo_stack) > self.MAX_UNDO_LEVELS:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self, current: PlaylistSnapshot) -> PlaylistSnapshot | None:
        """Restore previous state and push current to redo stack."""
        if not self._undo_stack:
            return None
        previous = self._undo_stack.pop()
        self._redo_stack.append(current)
        return previous

    def redo(self, current: PlaylistSnapshot) -> PlaylistSnapshot | None:
        """Restore next state and push current to undo stack."""
        if not self._redo_stack:
            return None
        next_state = self._redo_stack.pop()
        self._undo_stack.append(current)
        return next_state

    def can_undo(self) -> bool:
        """Return True if there are states to undo."""
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        """Return True if there are states to redo."""
        return len(self._redo_stack) > 0
