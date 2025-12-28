#!/usr/bin/env python3
"""Event type definitions for Platyplaty."""

from enum import Enum

from pydantic import BaseModel, ConfigDict


class StderrEventType(Enum):
    """Types of PLATYPLATY stderr events."""

    DISCONNECT = "DISCONNECT"
    AUDIO_ERROR = "AUDIO_ERROR"
    QUIT = "QUIT"


class StderrEvent(BaseModel):
    """A parsed PLATYPLATY stderr event."""

    model_config = ConfigDict(extra="forbid")

    source: str
    event: StderrEventType
    reason: str
