"""Startup sequence for PlatyplatyApp."""

import asyncio
import signal
from typing import TYPE_CHECKING

from platyplaty.auto_advance import auto_advance_loop, load_preset_with_retry
from platyplaty.dispatch_tables import build_renderer_dispatch_table
from platyplaty.event_loop import stderr_monitor_task
from platyplaty.messages import LogMessage
from platyplaty.renderer import start_renderer
from platyplaty.socket_client import SocketClient

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


async def perform_startup(app: "PlatyplatyApp") -> None:
    """Execute the startup sequence.

    Stage A: Start renderer, connect socket, send initial commands.
    Stage B: Start background workers.
    Stage C: Show window and optionally go fullscreen.

    Args:
        app: The PlatyplatyApp instance.

    Raises:
        Exception: On any startup failure after cleanup is performed.
    """
    # Stage A: Direct calls before workers start
    app._renderer_process = await start_renderer(app.socket_path)
    app._client = SocketClient()
    await app._client.connect(app.socket_path)
    await app._client.send_command(
        "CHANGE AUDIO SOURCE", audio_source=app.audio_source
    )
    await app._client.send_command("INIT")
    app._renderer_ready = True

    # Build dispatch table from stored keybindings
    app.renderer_dispatch_table = build_renderer_dispatch_table(
        next_preset_key=app._renderer_keybindings.next_preset,
        previous_preset_key=app._renderer_keybindings.previous_preset,
        quit_key=app._renderer_keybindings.quit,
    )

    # Load initial preset
    if not await load_preset_with_retry(app):
        app.post_message(
            LogMessage("All presets failed to load", level="warning")
        )

    # Stage B: Start workers
    app.run_worker(stderr_monitor_task(app), name="stderr_monitor")
    app.run_worker(auto_advance_loop(app), name="auto_advance")

    # Stage C: Send final startup commands
    await app._client.send_command("SHOW WINDOW")
    if app.fullscreen:
        await app._client.send_command("SET FULLSCREEN", enabled=True)


async def cleanup_on_startup_failure(app: "PlatyplatyApp") -> None:
    """Clean up resources after a startup failure.

    Terminates the renderer process if started and closes the client
    socket if connected.

    Args:
        app: The PlatyplatyApp instance.
    """
    if app._renderer_process is not None:
        app._renderer_process.terminate()
        await app._renderer_process.wait()
    if app._client is not None:
        app._client.close()
