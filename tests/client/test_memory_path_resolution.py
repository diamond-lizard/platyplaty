#!/usr/bin/env python3
"""Unit tests for memory path resolution.

Tests that selection memory is keyed by physical path (resolved),
not logical path, so symlinked directories share memory with targets.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.ui.nav_memory import save_current_memory
from platyplaty.ui.nav_state import NavigationState


class TestMemoryPathResolution:
    """Tests for physical path keying of selection memory."""

    def test_symlink_and_target_share_memory(self, tmp_path: Path) -> None:
        """Directory accessed via symlink shares memory with target."""
        target_dir = tmp_path / "target"
        target_dir.mkdir()
        (target_dir / "file1.milk").touch()
        (target_dir / "file2.milk").touch()

        symlink_dir = tmp_path / "link"
        symlink_dir.symlink_to(target_dir)

        state = NavigationState(symlink_dir)
        state.selected_name = "file2.milk"
        save_current_memory(state)

        target_key = str(target_dir.resolve())
        assert target_key in state._directory_memory
        assert state._directory_memory[target_key].selected_name == "file2.milk"

    def test_lookup_via_target_retrieves_symlink_memory(
        self, tmp_path: Path
    ) -> None:
        """Memory saved via symlink is retrievable via target path."""
        target_dir = tmp_path / "target"
        target_dir.mkdir()
        (target_dir / "preset.milk").touch()

        symlink_dir = tmp_path / "link"
        symlink_dir.symlink_to(target_dir)

        state = NavigationState(symlink_dir)
        state.selected_name = "preset.milk"
        state.scroll_offset = 5
        save_current_memory(state)

        resolved_key = str(symlink_dir.resolve())
        target_key = str(target_dir.resolve())
        assert resolved_key == target_key
        assert state._directory_memory[target_key].selected_name == "preset.milk"
        assert state._directory_memory[target_key].scroll_offset == 5

    def test_both_paths_resolve_to_same_key(self, tmp_path: Path) -> None:
        """Symlink path and target path resolve to same memory key."""
        target_dir = tmp_path / "data"
        target_dir.mkdir()
        (target_dir / "a.milk").touch()

        symlink_dir = tmp_path / "alias"
        symlink_dir.symlink_to(target_dir)

        assert str(symlink_dir.resolve()) == str(target_dir.resolve())
