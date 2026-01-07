#!/usr/bin/env python3
"""Configuration type definitions for Platyplaty."""

from pydantic import BaseModel, ConfigDict, Field

from platyplaty.types.keybindings import Keybindings


class Config(BaseModel):
    """Configuration for the Platyplaty visualizer.

    Attributes:
        preset_dirs: List of directories containing .milk preset files.
        audio_source: PulseAudio source name for audio capture.
        preset_duration: Seconds to display each preset before advancing.
        shuffle: Whether to randomize playlist order.
        loop: Whether to loop the playlist when reaching the end.
        fullscreen: Whether to start in fullscreen mode.
        keybindings: Keybindings for renderer and terminal.
    """

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    preset_dirs: list[str] = Field(alias="preset-dirs")
    audio_source: str = Field(default="@DEFAULT_SINK@.monitor", alias="audio-source")
    preset_duration: int = Field(default=30, ge=1, strict=True, alias="preset-duration")
    shuffle: bool = False
    loop: bool = True
    fullscreen: bool = False
    keybindings: Keybindings = Field(default_factory=Keybindings)
