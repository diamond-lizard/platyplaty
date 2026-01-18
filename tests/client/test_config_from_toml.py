#!/usr/bin/env python3
"""Unit tests for loading Config from TOML files."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.config import load_config


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
