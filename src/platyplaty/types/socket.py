#!/usr/bin/env python3
"""Socket-related type definitions for Platyplaty."""

from pydantic import BaseModel, ConfigDict


class StatusData(BaseModel):
    """Data returned by GET STATUS command."""

    model_config = ConfigDict(extra="forbid")

    audio_source: str
    audio_connected: bool
    preset_path: str
    visible: bool
    fullscreen: bool


class CommandResponse(BaseModel):
    """Response from the renderer for a command."""

    model_config = ConfigDict(extra="forbid")

    id: int | None
    success: bool
    data: dict[str, object] | None = None
    error: str | None = None
