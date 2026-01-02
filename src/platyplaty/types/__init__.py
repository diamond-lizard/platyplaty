#!/usr/bin/env python3
"""Type definitions for Platyplaty."""

from platyplaty.types.config import (
    ClientKeybindings,
    Config,
    Keybindings,
    RendererKeybindings,
)
from platyplaty.types.events import (
    KeyPressedEvent,
    ReasonEvent,
    StderrEvent,
)
from platyplaty.types.socket import CommandResponse, StatusData

__all__ = [
    "CommandResponse",
    "Config",
    "StatusData",
    "StderrEvent",
    "KeyPressedEvent",
    "ReasonEvent",
    "ClientKeybindings",
    "Keybindings",
    "RendererKeybindings",
]
