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

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    preset_dirs: list[str] = Field(alias="preset-dirs")
    audio_source: str = Field(default="@DEFAULT_SINK@.monitor", alias="audio-source")
    preset_duration: int = Field(default=30, ge=1, alias="preset-duration")
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
