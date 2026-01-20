#!/usr/bin/env python3
"""Clear playlist command handler.

Implements the :clear command for clearing the playlist.
"""

from typing import TYPE_CHECKING

from platyplaty.playlist_snapshot import push_undo_snapshot

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext


async def execute(
    ctx: "AppContext", app: "PlatyplatyApp"
) -> tuple[bool, str | None]:
    """Execute the :clear command.

    If playlist has unsaved changes, shows confirmation prompt.
    Otherwise clears immediately.

    Args:
        ctx: Application context.
        app: The Textual application.

    Returns:
        Tuple of (success, error_message). error_message is None on success.
    """
    if ctx.playlist.dirty_flag:
        await show_unsaved_changes_prompt(ctx, app)
        return (True, None)
    await perform_clear(ctx)
    return (True, None)


async def show_unsaved_changes_prompt(
    ctx: "AppContext", app: "PlatyplatyApp"
) -> None:
    """Show confirmation prompt for unsaved changes."""
    from platyplaty.ui.confirmation_prompt import ConfirmationPrompt

    prompt = app.query_one(ConfirmationPrompt)
    msg = (
        "There are unsaved changes in the currently loaded playlist, "
        "clear anyway (y/n)?"
    )

    async def on_response(confirmed: bool) -> None:
        if confirmed:
            await perform_clear(ctx)

    prompt.show_prompt(msg, on_response)


async def perform_clear(ctx: "AppContext") -> None:
    """Perform the actual clear operation."""
    push_undo_snapshot(ctx)
    ctx.playlist.clear()
    if ctx.autoplay_manager is not None:
        ctx.autoplay_manager.stop_autoplay()
