#!/usr/bin/env python3
"""Configuration type definitions for Platyplaty."""

from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

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

    @model_validator(mode="after")
    def _require_transition_type(self) -> Self:
        """Validate that transition_type is specified."""
        if self.renderer.transition_type is None:
            msg = "transition-type is required in [renderer] section"
            raise ValueError(msg)
        return self
