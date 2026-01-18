#!/usr/bin/env python3
"""Unit tests for generate_config.py output validation.

Tests that the generated config is valid TOML and can be loaded
by the config system.
"""

import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.config import load_config
from platyplaty.generate_config import EXAMPLE_CONFIG, generate_config


class TestGenerateConfigOutput:
    """Tests for generate_config output validation."""

    def test_example_config_is_valid_toml(self, tmp_path: Path) -> None:
        """Generated config should be valid TOML."""
        config_file = tmp_path / "config.toml"
        config_file.write_text(EXAMPLE_CONFIG)
        config = load_config(str(config_file))
        assert config is not None

    def test_example_config_has_correct_defaults(self, tmp_path: Path) -> None:
        """Generated config should load with expected default values."""
        config_file = tmp_path / "config.toml"
        config_file.write_text(EXAMPLE_CONFIG)
        config = load_config(str(config_file))
        assert config.renderer.audio_source == "@DEFAULT_SINK@.monitor"
        assert config.renderer.fullscreen is False
        assert config.keybindings.globals.quit == ["q"]
        assert config.keybindings.playlist.preset_duration == 30

    def test_generate_config_to_file(self, tmp_path: Path) -> None:
        """generate_config should write valid config to file."""
        config_file = tmp_path / "output.toml"
        generate_config(str(config_file))
        assert config_file.exists()
        config = load_config(str(config_file))
        assert config.keybindings.globals.switch_focus == ["tab"]

    def test_generate_config_refuses_overwrite(self, tmp_path: Path) -> None:
        """generate_config should refuse to overwrite existing file."""
        config_file = tmp_path / "existing.toml"
        config_file.write_text("existing content")
        with pytest.raises(FileExistsError):
            generate_config(str(config_file))
