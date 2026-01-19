#!/usr/bin/env python3
"""Tests for state restoration (TASK-05900)."""

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


class TestStateRestoration:
    """Tests for state restoration during undo/redo."""

    def test_undo_restores_presets(self) -> None:
        """Undo should restore playlist contents."""
        manager = UndoManager()
        original = (Path("/a.milk"), Path("/b.milk"))
        manager.push_undo(make_snapshot(presets=original))
        restored = manager.undo(make_snapshot(presets=()))
        assert restored is not None
        assert restored.presets == original

    def test_undo_restores_selection_index(self) -> None:
        """Undo should restore selection index."""
        manager = UndoManager()
        manager.push_undo(make_snapshot(selection=5))
        restored = manager.undo(make_snapshot(selection=10))
        assert restored is not None
        assert restored.selection_index == 5

    def test_undo_restores_playing_index(self) -> None:
        """Undo should restore playing index."""
        manager = UndoManager()
        manager.push_undo(make_snapshot(playing=3))
        restored = manager.undo(make_snapshot(playing=7))
        assert restored is not None
        assert restored.playing_index == 3

    def test_undo_restores_filename(self) -> None:
        """Undo should restore associated filename."""
        manager = UndoManager()
        original_file = Path("/my/playlist.platy")
        manager.push_undo(make_snapshot(filename=original_file))
        restored = manager.undo(make_snapshot(filename=None))
        assert restored is not None
        assert restored.associated_filename == original_file

    def test_undo_restores_dirty_flag(self) -> None:
        """Undo should restore dirty flag."""
        manager = UndoManager()
        manager.push_undo(make_snapshot(dirty=True))
        restored = manager.undo(make_snapshot(dirty=False))
        assert restored is not None
        assert restored.dirty_flag is True

    def test_undo_returns_none_when_empty(self) -> None:
        """Undo should return None when stack is empty."""
        manager = UndoManager()
        result = manager.undo(make_snapshot())
        assert result is None

    def test_redo_returns_none_when_empty(self) -> None:
        """Redo should return None when stack is empty."""
        manager = UndoManager()
        result = manager.redo(make_snapshot())
        assert result is None
