#!/usr/bin/env python3
"""Unit tests for Config default values."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.types.config import Config


class TestConfigDefaults:
    """Tests for Config with all default values."""

    def test_config_empty_creates_defaults(self) -> None:
        """Empty config should create all defaults."""
        config = Config()
        assert config.playlist is None
        assert config.renderer.audio_source == "@DEFAULT_SINK@.monitor"
        assert config.renderer.fullscreen is False

    def test_keybindings_global_defaults(self) -> None:
        """Global keybindings should have correct defaults."""
        config = Config()
        kb = config.keybindings.globals
        assert kb.switch_focus == ["tab"]
        assert kb.quit == ["q"]
        assert kb.navigate_up == ["k", "up"]
        assert kb.navigate_down == ["j", "down"]
        assert kb.open_selected == ["l", "right"]
        assert kb.view_errors == ["e"]
        assert kb.play_selection == ["enter"]

    def test_keybindings_file_browser_defaults(self) -> None:
        """File browser keybindings should have correct defaults."""
        config = Config()
        kb = config.keybindings.file_browser
        assert kb.open_parent == ["h", "left"]
        assert kb.add_preset_or_load_playlist == ["a"]
        assert kb.play_previous_preset == ["shift+k"]
        assert kb.play_next_preset == ["shift+j"]

    def test_keybindings_playlist_defaults(self) -> None:
        """Playlist keybindings should have correct defaults."""
        config = Config()
        kb = config.keybindings.playlist
        assert kb.play_previous == ["shift+k"]
        assert kb.play_next == ["shift+j"]
        assert kb.reorder_up == ["ctrl+k"]
        assert kb.reorder_down == ["ctrl+j"]
        assert kb.delete_from_playlist == ["shift+d", "delete"]
        assert kb.undo == ["u"]
        assert kb.redo == ["ctrl+r"]
        assert kb.preset_duration == 30

    def test_keybindings_error_view_defaults(self) -> None:
        """Error view keybindings should have correct defaults."""
        config = Config()
        kb = config.keybindings.error_view
        assert kb.clear_errors == ["c"]
