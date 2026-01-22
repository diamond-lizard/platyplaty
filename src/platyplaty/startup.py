#!/usr/bin/env python3
"""Startup sequence integration for Platyplaty.

This module provides the entry point for running Platyplaty with a
configuration file.
"""

import sys

from platyplaty.config import load_config
from platyplaty.errors import StartupError
from platyplaty.run_sequence import run_startup_sequence
from platyplaty.types import Config


def run_with_config(config_path: str, path_argument: str | None) -> int:
    """Run the visualizer with the given config file.

    Args:
        config_path: Path to the TOML configuration file.
        path_argument: Optional path to directory or .platy playlist file.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    try:
        config = _load_and_validate_config(config_path)
        run_startup_sequence(config, path_argument)
        return 0
    except KeyboardInterrupt:
        return 1
    except StartupError as e:
        sys.stderr.write(f"Error: {e}\n")
        return 1


def _load_and_validate_config(config_path: str) -> Config:
    """Load and validate the config file.

    Args:
        config_path: Path to the TOML configuration file.

    Returns:
        Validated Config object.

    Raises:
        StartupError: If config loading or validation fails.
    """
    try:
        return load_config(config_path)
    except FileNotFoundError:
        raise StartupError(f"Config file not found: {config_path}") from None
    except Exception as e:
        raise StartupError(f"Config error: {e}") from None
