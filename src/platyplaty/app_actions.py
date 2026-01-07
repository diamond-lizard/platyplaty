"""Preset navigation actions for PlatyplatyApp."""

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

from platyplaty.messages import LogMessage
from platyplaty.socket_exceptions import RendererError

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp


async def load_preset_by_direction(
    app: "PlatyplatyApp",
    get_preset: Callable[[], Path | None],
    direction: str,
) -> None:
    """Load the next or previous preset based on direction.

    This is the shared implementation for both action_next_preset and
    action_previous_preset. It handles the common guards, loads the
    preset, and posts error messages on failure.

    Args:
        app: The PlatyplatyApp instance.
        get_preset: Callable that returns the preset path (playlist.next
            or playlist.previous).
        direction: Description for error messages ("next" or "previous").
    """
    if not app._renderer_ready or not app._client or app._exiting:
        return
    path = get_preset()
    if path is None:
        return
    try:
        await app._client.send_command("LOAD PRESET", path=str(path))
    except RendererError as e:
        app.post_message(
            LogMessage(f"Failed to load {direction} preset: {e}", level="warning")
        )
