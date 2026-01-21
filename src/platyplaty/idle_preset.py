"""Idle preset loading functions."""

from typing import TYPE_CHECKING

from platyplaty.auto_advance import load_preset_with_retry
from platyplaty.messages import LogMessage

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext


async def load_idle_preset(ctx: "AppContext") -> None:
    """Load the idle preset (no visualization).

    Sends LOAD PRESET command with idle:// URL to the renderer.

    Args:
        ctx: The AppContext instance with runtime state.
    """
    if ctx.client is not None:
        await ctx.client.send_command("LOAD PRESET", path="idle://")


async def load_initial_preset(ctx: "AppContext", app: "PlatyplatyApp") -> None:
    """Load initial preset or idle if playlist is empty or all fail.

    Attempts to load the first preset in the playlist. If the playlist
    is empty or all presets fail to load, loads the idle preset.

    Args:
        ctx: The AppContext instance with runtime state.
        app: The PlatyplatyApp instance for logging.
    """
    if not ctx.playlist.presets:
        await load_idle_preset(ctx)
        return
    if await load_preset_with_retry(ctx, app):
        return
    app.post_message(LogMessage("All presets failed to load", level="warning"))
    await load_idle_preset(ctx)
