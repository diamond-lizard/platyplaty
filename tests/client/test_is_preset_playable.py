#!/usr/bin/env python3
"""Unit tests for is_preset_playable function.

Tests that is_preset_playable correctly handles bad presets (crashed
the renderer), missing presets, and valid presets.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.autoplay_helpers import is_preset_playable
from platyplaty.bad_presets import _bad_presets, mark_preset_as_bad


class TestIsPresetPlayable:
    """Tests for is_preset_playable function."""

    def setup_method(self) -> None:
        """Clear the bad presets set before each test."""
        _bad_presets.clear()

    def test_valid_preset_is_playable(self, tmp_path: Path) -> None:
        """Valid readable file is playable."""
        preset = tmp_path / "good.milk"
        preset.write_text("content")
        assert is_preset_playable(preset) is True

    def test_missing_preset_not_playable(self, tmp_path: Path) -> None:
        """Non-existent file is not playable."""
        preset = tmp_path / "missing.milk"
        assert is_preset_playable(preset) is False

    def test_bad_preset_not_playable(self, tmp_path: Path) -> None:
        """Preset marked as bad is not playable."""
        preset = tmp_path / "bad.milk"
        preset.write_text("content")
        mark_preset_as_bad(preset)
        assert is_preset_playable(preset) is False

    def test_broken_symlink_not_playable(self, tmp_path: Path) -> None:
        """Broken symlink is not playable."""
        link = tmp_path / "broken.milk"
        link.symlink_to(tmp_path / "nonexistent.milk")
        assert is_preset_playable(link) is False

    def test_symlink_to_bad_preset_not_playable(
        self, tmp_path: Path
    ) -> None:
        """Symlink to bad preset is not playable."""
        preset = tmp_path / "original.milk"
        preset.write_text("content")
        symlink = tmp_path / "link.milk"
        symlink.symlink_to(preset)
        mark_preset_as_bad(preset)
        assert is_preset_playable(symlink) is False
