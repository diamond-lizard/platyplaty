#!/usr/bin/env python3
"""Configuration module for Platyplaty.

Handles loading and validation of TOML configuration files using pydantic.
"""

import tomllib

from pydantic import BaseModel, ConfigDict, Field


class Config(BaseModel):
    """Configuration for the Platyplaty visualizer.

    Attributes:
        preset_dirs: List of directories containing .milk preset files.
        audio_source: PulseAudio source name for audio capture.
        preset_duration: Seconds to display each preset before advancing.
        shuffle: Whether to randomize playlist order.
        loop: Whether to loop the playlist when reaching the end.
        fullscreen: Whether to start in fullscreen mode.
    """

    model_config = ConfigDict(extra="forbid")

    preset_dirs: list[str]
    audio_source: str = "@DEFAULT_SINK@.monitor"
    preset_duration: int = Field(default=30, ge=1)
    shuffle: bool = False
    loop: bool = True
    fullscreen: bool = False


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
