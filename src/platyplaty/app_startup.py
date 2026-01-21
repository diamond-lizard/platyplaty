"""Startup sequence for PlatyplatyApp."""

import asyncio
import signal
from typing import TYPE_CHECKING

from platyplaty.auto_advance import auto_advance_loop, load_preset_with_retry
from platyplaty.event_loop import stderr_monitor_task
from platyplaty.messages import LogMessage
from platyplaty.renderer import start_renderer
from platyplaty.socket_client import SocketClient

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext


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


async def perform_startup(ctx: "AppContext", app: "PlatyplatyApp") -> None:
    """Execute the startup sequence.

    Stage A: Start renderer, connect socket, send initial commands.
    Stage B: Start background workers.
    Stage C: Show window and optionally go fullscreen.

    Args:
        ctx: The AppContext instance with runtime state.
        app: The PlatyplatyApp instance (for post_message, run_worker).

    Raises:
        Exception: On any startup failure after cleanup is performed.
    """
    # Stage A: Direct calls before workers start
    ctx.renderer_process = await start_renderer(ctx.config.socket_path)
    ctx.client = SocketClient()
    await ctx.client.connect(ctx.config.socket_path)
    await ctx.client.send_command(
        "CHANGE AUDIO SOURCE", audio_source=ctx.config.audio_source
    )
    await ctx.client.send_command("INIT")
    ctx.renderer_ready = True

    # Load initial preset (or idle if playlist is empty)
    if ctx.playlist.presets:
        if not await load_preset_with_retry(ctx, app):
            app.post_message(
                LogMessage("All presets failed to load", level="warning")
            )
            await _load_idle_preset(ctx)
    else:
        await _load_idle_preset(ctx)

    # Stage B: Start workers
    app.run_worker(stderr_monitor_task(ctx, app), name="stderr_monitor")
    app.run_worker(auto_advance_loop(ctx, app), name="auto_advance")

    # Stage C: Send final startup commands
    await ctx.client.send_command("SHOW WINDOW")
    if ctx.config.fullscreen:
        await ctx.client.send_command("SET FULLSCREEN", enabled=True)


async def cleanup_on_startup_failure(ctx: "AppContext") -> None:
    """Clean up resources after a startup failure.

    Terminates the renderer process if started and closes the client
    socket if connected.

    Args:
        ctx: The AppContext instance with runtime state.
    """
    if ctx.renderer_process is not None:
        ctx.renderer_process.terminate()
        await ctx.renderer_process.wait()
    if ctx.client is not None:
        ctx.client.close()


async def on_mount_handler(ctx: "AppContext", app: "PlatyplatyApp") -> None:
    """Handle app mount event with startup and error handling.

    Sets up signal handlers and performs startup sequence. On failure,
    cleans up resources and exits the app with an error message.

    Args:
        ctx: The AppContext instance with runtime state.
        app: The PlatyplatyApp instance.
    """
    setup_signal_handlers(app)
    try:
        await perform_startup(ctx, app)
    except Exception as e:
        await cleanup_on_startup_failure(ctx)
        app.exit(message=str(e))


async def _load_idle_preset(ctx: "AppContext") -> None:
    """Load the idle preset (no visualization).

    Sends LOAD PRESET command with idle:// URL to the renderer.

    Args:
        ctx: The AppContext instance with runtime state.
    """
    await ctx.client.send_command("LOAD PRESET", path="idle://")
