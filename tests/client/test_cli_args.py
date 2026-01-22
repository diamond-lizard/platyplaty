#!/usr/bin/env python3
"""Unit tests for CLI argument parsing.

Tests that the main CLI correctly parses the optional path argument
and passes it to the startup functions.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.main import main


class TestCliPathArgument:
    """Tests for the optional path positional argument."""

    def test_path_argument_passed_to_run_with_config(self, tmp_path: Path) -> None:
        """Path argument should be passed to run_with_config."""
        runner = CliRunner()
        config_file = tmp_path / "test.toml"
        config_file.touch()
        with patch("platyplaty.startup.run_with_config") as mock_run:
            mock_run.return_value = 0
            result = runner.invoke(
                main,
                ["--config-file", str(config_file), "/some/path"],
            )
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert call_args[0][1] == "/some/path"

    def test_no_path_argument_passes_none(self, tmp_path: Path) -> None:
        """Missing path argument should pass None to run_with_config."""
        runner = CliRunner()
        config_file = tmp_path / "test.toml"
        config_file.touch()
        with patch("platyplaty.startup.run_with_config") as mock_run:
            mock_run.return_value = 0
            result = runner.invoke(main, ["--config-file", str(config_file)])
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert call_args[0][1] is None

    def test_path_argument_with_spaces(self, tmp_path: Path) -> None:
        """Path with spaces should be handled correctly."""
        runner = CliRunner()
        config_file = tmp_path / "test.toml"
        config_file.touch()
        with patch("platyplaty.startup.run_with_config") as mock_run:
            mock_run.return_value = 0
            result = runner.invoke(
                main,
                ["--config-file", str(config_file), "/path/with spaces/file.platy"],
            )
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert call_args[0][1] == "/path/with spaces/file.platy"

    def test_path_argument_not_passed_with_generate_config(
        self,
        tmp_path: Path,
    ) -> None:
        """Path argument should not affect --generate-config mode."""
        runner = CliRunner()
        config_file = tmp_path / "test.toml"
        result = runner.invoke(
            main,
            ["--generate-config", str(config_file), "/ignored/path"],
        )
        # generate_config ignores path argument; file should be created
        assert config_file.exists()
