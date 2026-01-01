#!/usr/bin/env python3
"""Type definitions for Platyplaty."""

from platyplaty.types.config import ClientKeybindings, Config, Keybindings, RendererKeybindings
from platyplaty.types.events import StderrEvent, StderrEventType
from platyplaty.types.socket import CommandResponse, StatusData

__all__ = [
    "CommandResponse",
    "Config",
    "StatusData",
    "StderrEvent",
    "StderrEventType",
    "ClientKeybindings",
    "Keybindings",
    "RendererKeybindings",
]
