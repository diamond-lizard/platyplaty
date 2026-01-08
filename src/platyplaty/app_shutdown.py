"""Shutdown logic for PlatyplatyApp."""

import contextlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext


async def perform_graceful_shutdown(ctx: "AppContext", app: "PlatyplatyApp") -> None:
    """Shut down the application gracefully.

    Sets the exiting flag, sends QUIT command to the renderer (if
    reachable), closes the socket, and exits the application.

    Args:
        ctx: The AppContext instance with runtime state.
        app: The PlatyplatyApp instance (for exit).
    """
    ctx.exiting = True
    if ctx.client:
        with contextlib.suppress(ConnectionError):
            await ctx.client.send_command("QUIT")
        ctx.client.close()
    app.exit()
