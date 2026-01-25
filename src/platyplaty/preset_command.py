#!/usr/bin/env python3
"""Preset loading command with crash tracking.

This module provides the send_load_preset function which tracks the preset
path before sending the LOAD PRESET command. This tracking enables crash
detection to identify which preset caused a renderer crash.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app_context import AppContext


async def send_load_preset(ctx: AppContext, path: Path | str) -> None:
    """Send LOAD PRESET command with crash tracking.

    This function sets ctx.preset_sent_to_renderer before sending the
    command. This allows crash detection code to identify which preset
    caused the renderer to crash.

    All code that loads presets should use load_preset() (added in Phase
    600) instead of calling this function directly. This function is
    internal infrastructure for crash tracking.

    Args:
        ctx: Application context with client for sending commands.
        path: Preset file path (Path) or special URL like "idle://" (str).
    """
    ctx.preset_sent_to_renderer = path
    await ctx.client.send_command("LOAD PRESET", path=str(path))
