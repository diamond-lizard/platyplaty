#!/usr/bin/env python3
"""Type definitions for Platyplaty."""

from platyplaty.types.config import Config
from platyplaty.types.events import (
    KeyPressedEvent,
    ReasonEvent,
    StderrEvent,
)
from platyplaty.types.keybindings import Keybindings
from platyplaty.types.socket import CommandResponse, StatusData

__all__ = [
    "CommandResponse",
    "Config",
    "StatusData",
    "StderrEvent",
    "KeyPressedEvent",
    "ReasonEvent",
    "Keybindings",
]
