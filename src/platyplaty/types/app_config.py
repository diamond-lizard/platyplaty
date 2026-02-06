#!/usr/bin/env python3
"""Application configuration dataclass for Platyplaty."""

from dataclasses import dataclass
from typing import Literal

from platyplaty.types.keybindings import Keybindings


@dataclass(frozen=True)
class AppConfig:
    """Immutable application configuration.

    Contains all configuration values needed by the application.
    This is a frozen dataclass to ensure configuration is immutable
    after creation.

    Attributes:
        socket_path: Path to the Unix domain socket for renderer communication.
        audio_source: PulseAudio source name for audio capture.
        preset_duration: Seconds to display each preset before advancing.
        fullscreen: Whether to start in fullscreen mode.
        keybindings: Keybindings for renderer, client, and file browser.
        transition_type: Transition type for preset loading ("soft" or "hard").
    """

    socket_path: str
    audio_source: str
    preset_duration: float
    fullscreen: bool
    keybindings: Keybindings
    transition_type: Literal["soft", "hard"]
