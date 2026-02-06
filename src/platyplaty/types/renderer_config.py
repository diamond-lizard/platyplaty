#!/usr/bin/env python3
"""Renderer configuration for Platyplaty."""

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class RendererConfig(BaseModel):
    """Non-keybinding renderer settings.

    Attributes:
        audio_source: PulseAudio source name for audio capture.
        fullscreen: Whether to start in fullscreen mode.
        transition_type: Transition type for preset loading ("soft" or "hard").
    """

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    audio_source: str = Field(
        default="@DEFAULT_SINK@.monitor", alias="audio-source"
    )
    fullscreen: bool = False
    transition_type: Literal["soft", "hard"] = Field(
        alias="transition-type"
    )
