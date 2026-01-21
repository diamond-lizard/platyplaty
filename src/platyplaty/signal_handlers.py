"""Signal handlers for graceful shutdown."""

import asyncio
import signal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp


def setup_signal_handlers(app: "PlatyplatyApp") -> None:
    """Register signal handlers for graceful shutdown.

    Registers SIGINT and SIGTERM handlers that trigger graceful_shutdown.

    Args:
        app: The PlatyplatyApp instance.
    """
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(
        signal.SIGINT,
        lambda: asyncio.create_task(app.graceful_shutdown()),
    )
    loop.add_signal_handler(
        signal.SIGTERM,
        lambda: asyncio.create_task(app.graceful_shutdown()),
    )
