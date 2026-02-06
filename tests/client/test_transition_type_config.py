#!/usr/bin/env python3
"""Unit tests for transition-type config validation."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.config import load_config


class TestTransitionTypeConfig:
    """Tests for transition-type configuration validation."""

    def test_missing_transition_type_raises_error(
        self, tmp_path: Path
    ) -> None:
        """Missing transition-type should raise a validation error."""
        config_file = tmp_path / "config.toml"
        config_file.write_text("[renderer]\n")
        with pytest.raises(Exception, match="transition"):
            load_config(str(config_file))

    def test_invalid_transition_type_raises_error(
        self, tmp_path: Path
    ) -> None:
        """Invalid transition-type should raise a validation error."""
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            '[renderer]\ntransition-type = "invalid"\n'
        )
        with pytest.raises(Exception, match="transition"):
            load_config(str(config_file))

    def test_soft_transition_type_accepted(
        self, tmp_path: Path
    ) -> None:
        """transition-type = "soft" should be accepted."""
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            '[renderer]\ntransition-type = "soft"\n'
        )
        config = load_config(str(config_file))
        assert config.renderer.transition_type == "soft"

    def test_hard_transition_type_accepted(
        self, tmp_path: Path
    ) -> None:
        """transition-type = "hard" should be accepted."""
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            '[renderer]\ntransition-type = "hard"\n'
        )
        config = load_config(str(config_file))
        assert config.renderer.transition_type == "hard"
