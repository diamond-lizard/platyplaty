#!/usr/bin/env python3
"""Tests for undo stack 1000 level limit (TASK-05700)."""

from pathlib import Path

from platyplaty.undo import PlaylistSnapshot, UndoManager


def make_snapshot(
    presets: tuple[Path, ...] = (),
    selection: int = 0,
    playing: int | None = 0,
    filename: Path | None = None,
    dirty: bool = False,
) -> PlaylistSnapshot:
    """Create a snapshot with default values."""
    return PlaylistSnapshot(presets, selection, playing, filename, dirty)


def _count_undos(manager: UndoManager) -> int:
    """Count how many undos are available."""
    count = 0
    while manager.can_undo():
        manager.undo(make_snapshot())
        count += 1
    return count


def _get_all_selection_indices(manager: UndoManager) -> list[int]:
    """Extract all selection indices from undo stack."""
    indices = []
    while manager.can_undo():
        s = manager.undo(make_snapshot())
        if s:
            indices.append(s.selection_index)
    return indices


class TestUndoStackLimit:
    """Tests for undo stack 1000 level limit."""

    def test_stack_accepts_up_to_1000_entries(self) -> None:
        """Undo stack should hold exactly 1000 entries."""
        manager = UndoManager()
        for i in range(1000):
            manager.push_undo(make_snapshot(selection=i))
        assert manager.can_undo()
        assert _count_undos(manager) == 1000

    def test_stack_discards_oldest_when_exceeds_1000(self) -> None:
        """Push beyond 1000 should discard oldest entry."""
        manager = UndoManager()
        for i in range(1001):
            manager.push_undo(make_snapshot(selection=i))
        assert _count_undos(manager) == 1000

    def test_oldest_entry_discarded_is_first_pushed(self) -> None:
        """When exceeding limit, first pushed entry should be gone."""
        manager = UndoManager()
        for i in range(1001):
            manager.push_undo(make_snapshot(selection=i))
        indices = _get_all_selection_indices(manager)
        assert 0 not in indices
        assert 1 in indices
