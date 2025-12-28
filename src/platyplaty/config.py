#!/usr/bin/env python3
"""Configuration module for Platyplaty.

Handles loading and validation of TOML configuration files using pydantic.
"""

import tomllib

from platyplaty.types import Config


def load_config(path: str) -> Config:
    """Load and validate configuration from a TOML file.

    Args:
        path: Path to the TOML configuration file.

    Returns:
        Validated Config object.

    Raises:
        FileNotFoundError: If the config file doesn't exist.
        tomllib.TOMLDecodeError: If the file contains invalid TOML.
        pydantic.ValidationError: If config values are invalid.
    """
    with open(path, "rb") as f:
        data = tomllib.load(f)
    return Config(**data)
