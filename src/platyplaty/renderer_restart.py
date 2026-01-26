#!/usr/bin/env python3
"""Renderer restart functionality for crash recovery.

This module provides the ensure_renderer_running function that restarts
the renderer when it has crashed, allowing the user to continue using
the application by loading a new preset.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp
    from platyplaty.app_context import AppContext


async def ensure_renderer_running(ctx: "AppContext", app: "PlatyplatyApp") -> bool:
    """Ensure the renderer is running, restarting it if necessary.

    If the renderer process is already running, returns True immediately.
    If the renderer has crashed or never started, this function will:
    1. Start a new renderer process
    2. Create and connect a new socket client
    3. Send CHANGE AUDIO SOURCE and INIT commands
    4. Start a new stderr_monitor_task worker
    5. Set ctx.renderer_ready = True

    Args:
        ctx: Application context with renderer state.
        app: The Textual application instance for run_worker.

    Returns:
        True if renderer is running (either already was or successfully
        restarted), False if restart failed.
    """
    from platyplaty.event_loop import stderr_monitor_task
    from platyplaty.renderer import start_renderer
    from platyplaty.socket_client import SocketClient
    from platyplaty.socket_path import check_stale_socket
    from platyplaty.ui.command_line import CommandLine

    # Check if renderer is already running
    if ctx.renderer_process is not None and ctx.renderer_process.returncode is None:
        return True

    # Renderer not running - restart it
    try:
        check_stale_socket(ctx.config.socket_path)
        ctx.renderer_process = await start_renderer(ctx.config.socket_path)
        ctx.client = SocketClient()
        await ctx.client.connect(ctx.config.socket_path)
        await ctx.client.send_command(
            "CHANGE AUDIO SOURCE", audio_source=ctx.config.audio_source
        )
        await ctx.client.send_command("INIT")
        app.run_worker(stderr_monitor_task(ctx, app), name="stderr_monitor")
        ctx.renderer_ready = True
        return True
    except Exception:
        command_line = app.query_one("#command_line", CommandLine)
        command_line.show_persistent_message("Failed to start renderer.")
        return False
