"""Shutdown logic for PlatyplatyApp."""

import contextlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp


async def perform_graceful_shutdown(app: "PlatyplatyApp") -> None:
    """Shut down the application gracefully.

    Sets the exiting flag, sends QUIT command to the renderer (if
    reachable), closes the socket, and exits the application.

    Args:
        app: The PlatyplatyApp instance.
    """
    app._exiting = True
    if app._client:
        with contextlib.suppress(ConnectionError):
            await app._client.send_command("QUIT")
        app._client.close()
    app.exit()
