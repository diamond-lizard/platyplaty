#!/usr/bin/env python3
"""Unit tests for bad preset registry."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.bad_presets import (
    _bad_presets,
    mark_preset_as_bad,
    is_preset_bad,
)


class TestBadPresets:
    """Tests for bad preset registry functions."""

    def setup_method(self) -> None:
        """Clear the bad presets set before each test."""
        _bad_presets.clear()

    def test_mark_preset_as_bad(self, tmp_path: Path) -> None:
        """mark_preset_as_bad adds preset to registry."""
        preset = tmp_path / "bad.milk"
        preset.touch()
        mark_preset_as_bad(preset)
        assert preset.resolve() in _bad_presets

    def test_is_preset_bad_returns_false_initially(
        self, tmp_path: Path
    ) -> None:
        """is_preset_bad returns False for unmarked preset."""
        preset = tmp_path / "good.milk"
        preset.touch()
        assert is_preset_bad(preset) is False

    def test_is_preset_bad_returns_true_after_marking(
        self, tmp_path: Path
    ) -> None:
        """is_preset_bad returns True after marking."""
        preset = tmp_path / "bad.milk"
        preset.touch()
        mark_preset_as_bad(preset)
        assert is_preset_bad(preset) is True

    def test_symlink_resolves_to_same_path(self, tmp_path: Path) -> None:
        """Symlink to bad preset is also considered bad."""
        preset = tmp_path / "original.milk"
        preset.touch()
        symlink = tmp_path / "link.milk"
        symlink.symlink_to(preset)
        mark_preset_as_bad(preset)
        assert is_preset_bad(symlink) is True

    def test_marking_symlink_marks_target(self, tmp_path: Path) -> None:
        """Marking symlink as bad also marks the target."""
        preset = tmp_path / "original.milk"
        preset.touch()
        symlink = tmp_path / "link.milk"
        symlink.symlink_to(preset)
        mark_preset_as_bad(symlink)
        assert is_preset_bad(preset) is True
