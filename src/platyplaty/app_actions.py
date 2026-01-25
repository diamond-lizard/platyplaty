"""Preset navigation actions for PlatyplatyApp."""

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext


async def load_preset_by_direction(
    ctx: "AppContext",
    app: "PlatyplatyApp",
    get_preset: Callable[[], Path | None],
    direction: str,
) -> None:
    """Load the next or previous preset based on direction.

    This is the shared implementation for both action_next_preset and
    action_previous_preset. It handles the common guards, loads the
    preset, and posts error messages on failure.

    Args:
        ctx: The AppContext instance with runtime state.
        app: The PlatyplatyApp instance (for post_message).
        get_preset: Callable that returns the preset path (playlist.next
            or playlist.previous).
        direction: Description for error messages ("next" or "previous").
    """
    if ctx.exiting:
        return
    path = get_preset()
    if path is None:
        return
    from platyplaty.preset_command import load_preset
    success, error = await load_preset(ctx, app, path)
    if not success and error is not None:
        from platyplaty.ui.command_line import CommandLine
        cmd_line = app.query_one("#command_line", CommandLine)
        cmd_line.show_transient_error(error)
        ctx.error_log.append(error)
        from platyplaty.ui.status_line import StatusLine
        app.query_one("#status_line", StatusLine).update_error_indicator()
