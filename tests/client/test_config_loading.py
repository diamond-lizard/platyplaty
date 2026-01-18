#!/usr/bin/env python3
"""Unit tests for configuration loading with new section structure.

Tests Config loading with global, file-browser, playlist, and
error-view keybinding sections.
"""

import sys
import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.config import load_config
from platyplaty.types.config import Config
from platyplaty.types.keybindings import Keybindings


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


class TestConfigFromToml:
    """Tests for loading Config from TOML files."""

    def test_load_minimal_config(self, tmp_path: Path) -> None:
        """Load a minimal TOML config with all defaults."""
        config_file = tmp_path / "config.toml"
        config_file.write_text("")
        config = load_config(str(config_file))
        assert config.playlist is None
        assert config.keybindings.globals.quit == ["q"]

    def test_load_with_playlist_path(self, tmp_path: Path) -> None:
        """Load config with playlist path specified."""
        config_file = tmp_path / "config.toml"
        config_file.write_text('playlist = "/home/user/my.platy"')
        config = load_config(str(config_file))
        assert config.playlist == "/home/user/my.platy"

    def test_load_with_renderer_settings(self, tmp_path: Path) -> None:
        """Load config with renderer settings."""
        toml_content = '''
[renderer]
audio-source = "custom_source"
fullscreen = true
'''
        config_file = tmp_path / "config.toml"
        config_file.write_text(toml_content)
        config = load_config(str(config_file))
        assert config.renderer.audio_source == "custom_source"
        assert config.renderer.fullscreen is True

    def test_load_with_global_keybindings(self, tmp_path: Path) -> None:
        """Load config with custom global keybindings."""
        toml_content = '''
[keybindings.global]
quit = ["ctrl+q", "escape"]
'''
        config_file = tmp_path / "config.toml"
        config_file.write_text(toml_content)
        config = load_config(str(config_file))
        assert config.keybindings.globals.quit == ["ctrl+q", "escape"]
        assert config.keybindings.globals.navigate_up == ["k", "up"]

    def test_load_with_playlist_keybindings(self, tmp_path: Path) -> None:
        """Load config with custom playlist keybindings and duration."""
        toml_content = '''
[keybindings.playlist]
preset-duration = 60
shuffle-playlist = ["r"]
'''
        config_file = tmp_path / "config.toml"
        config_file.write_text(toml_content)
        config = load_config(str(config_file))
        assert config.keybindings.playlist.preset_duration == 60
        assert config.keybindings.playlist.shuffle_playlist == ["r"]
