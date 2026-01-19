#!/usr/bin/env python3
"""Tests for redo stack clearing on new action (TASK-05800)."""

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


class TestRedoStackClearing:
    """Tests for redo stack clearing on new action."""

    def test_redo_stack_clears_on_push(self) -> None:
        """Pushing new undo should clear redo stack."""
        manager = UndoManager()
        manager.push_undo(make_snapshot(selection=1))
        manager.push_undo(make_snapshot(selection=2))
        manager.undo(make_snapshot(selection=3))
        assert manager.can_redo()
        manager.push_undo(make_snapshot(selection=4))
        assert not manager.can_redo()

    def test_redo_stack_empty_initially(self) -> None:
        """Redo stack should be empty on new manager."""
        manager = UndoManager()
        assert not manager.can_redo()

    def test_redo_available_after_undo(self) -> None:
        """Redo should be available after an undo."""
        manager = UndoManager()
        manager.push_undo(make_snapshot(selection=1))
        manager.undo(make_snapshot(selection=2))
        assert manager.can_redo()

    def test_undo_stack_empty_initially(self) -> None:
        """Undo stack should be empty on new manager."""
        manager = UndoManager()
        assert not manager.can_undo()

    def test_undo_available_after_push(self) -> None:
        """Undo should be available after a push."""
        manager = UndoManager()
        manager.push_undo(make_snapshot())
        assert manager.can_undo()
