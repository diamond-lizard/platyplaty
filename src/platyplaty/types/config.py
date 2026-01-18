#!/usr/bin/env python3
"""Configuration type definitions for Platyplaty."""

from pydantic import BaseModel, ConfigDict, Field

from platyplaty.types.keybindings import Keybindings
from platyplaty.types.renderer_config import RendererConfig


class Config(BaseModel):
    """Configuration for the Platyplaty visualizer.

    Attributes:
        playlist: Optional path to .platy playlist file to load at startup.
        renderer: Renderer window settings (audio, fullscreen).
        keybindings: Keybindings for all sections.
    """

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    playlist: str | None = Field(default=None)
    renderer: RendererConfig = Field(default_factory=RendererConfig)
    keybindings: Keybindings = Field(default_factory=Keybindings)
