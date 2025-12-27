#!/usr/bin/env python3
"""Startup sequence integration for Platyplaty.

This module integrates all components into the complete startup sequence:
config loading, path resolution, playlist building, renderer startup,
socket connection, and main event loop.
"""

import asyncio
import sys
from pathlib import Path
from typing import TextIO

from platyplaty.auto_advance import auto_advance_loop, load_preset_with_retry
from platyplaty.config import Config, load_config
from platyplaty.event_loop import EventLoopState, stderr_monitor_task
from platyplaty.paths import UndefinedEnvVarError, expand_path, resolve_path
from platyplaty.playlist import (
    NoPresetsFoundError,
    Playlist,
    scan_preset_dirs,
    shuffle_presets,
)
from platyplaty.renderer import (
    RendererNotFoundError,
    find_renderer_binary,
    start_renderer,
)
from platyplaty.shutdown import (
    cancel_tasks,
    graceful_shutdown,
    register_signal_handlers,
)
from platyplaty.socket_client import SocketClient
from platyplaty.socket_path import (
    AlreadyRunningError,
    StaleSocketError,
    check_stale_socket,
    compute_socket_path,
)


class StartupError(Exception):
    """Raised when startup fails."""


def run_with_config(config_path: str) -> int:
    """Run the visualizer with the given config file.

    Args:
        config_path: Path to the TOML configuration file.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    try:
        config = _load_and_validate_config(config_path)
        _run_startup_sequence(config, sys.stderr)
        return 0
    except KeyboardInterrupt:
        return 1
    except StartupError as e:
        sys.stderr.write(f"Error: {e}\n")
        return 1


def _load_and_validate_config(config_path: str) -> Config:
    """Load and validate the config file.

    Args:
        config_path: Path to the TOML configuration file.

    Returns:
        Validated Config object.

    Raises:
        StartupError: If config loading or validation fails.
    """
    try:
        return load_config(config_path)
    except FileNotFoundError:
        raise StartupError(f"Config file not found: {config_path}") from None
    except Exception as e:
        raise StartupError(f"Config error: {e}") from None



def _expand_preset_dirs(preset_dirs: list[str]) -> list[str]:
    """Expand and resolve preset directory paths.

    Args:
        preset_dirs: List of directory paths from config.

    Returns:
        List of absolute paths.

    Raises:
        StartupError: If an environment variable is undefined.
    """
    result: list[str] = []
    for path in preset_dirs:
        try:
            expanded = expand_path(path)
        except UndefinedEnvVarError as e:
            raise StartupError(str(e)) from None
        result.append(resolve_path(expanded))
    return result


def _validate_preset_dirs(preset_dirs: list[str]) -> None:
    """Validate that all preset directories exist.

    Args:
        preset_dirs: List of absolute directory paths.

    Raises:
        StartupError: If any directory does not exist.
    """
    for path in preset_dirs:
        if not Path(path).is_dir():
            raise StartupError(f"Preset directory not found: {path}")


async def _async_main(
    socket_path: str,
    audio_source: str,
    playlist: Playlist,
    preset_duration: int,
    fullscreen: bool,
    output: TextIO,
) -> None:
    """Run the async portion of the startup sequence.

    Args:
        socket_path: Path to the Unix domain socket.
        audio_source: PulseAudio source for audio capture.
        playlist: The preset playlist.
        preset_duration: Seconds between preset changes.
        fullscreen: Whether to start in fullscreen mode.
        output: Output stream for status messages.
    """
    # Start renderer subprocess
    renderer_process = await start_renderer(socket_path)

    # Connect to socket
    client = SocketClient()
    await client.connect(socket_path)

    # Send CHANGE AUDIO SOURCE command
    await client.send_command("CHANGE AUDIO SOURCE", source=audio_source)

    # Send INIT command
    await client.send_command("INIT")

    # Attempt to load first preset; try next on failure
    preset_loaded = await load_preset_with_retry(client, playlist, output)
    if not preset_loaded:
        output.write("Warning: All presets failed to load; showing idle preset\n")
        output.flush()

    # Send SHOW WINDOW command
    await client.send_command("SHOW WINDOW")
    _window_visible = True

    # Send SET FULLSCREEN if configured
    if fullscreen:
        await client.send_command("SET FULLSCREEN", enabled=True)

    # Enter main event loop
    state = EventLoopState()
    loop = asyncio.get_event_loop()
    register_signal_handlers(loop, state)

    # Create background tasks
    stderr_task = asyncio.create_task(
        stderr_monitor_task(renderer_process, state, output)
    )
    advance_task = asyncio.create_task(
        auto_advance_loop(client, playlist, preset_duration, state, output)
    )

    try:
        # Wait for shutdown signal
        await state.shutdown_event.wait()
    finally:
        await cancel_tasks([stderr_task, advance_task])
        await graceful_shutdown(client)

def _run_startup_sequence(config: Config, output: TextIO) -> None:
    """Run the main startup sequence.

    Args:
        config: Validated configuration.
        output: Output stream for status messages.

    Raises:
        StartupError: If any startup step fails.
    """
    # Expand and resolve preset directory paths
    preset_dirs = _expand_preset_dirs(config.preset_dirs)
    _validate_preset_dirs(preset_dirs)

    # Scan preset directories and build playlist
    try:
        presets = scan_preset_dirs(preset_dirs)
    except NoPresetsFoundError as e:
        raise StartupError(str(e)) from None

    if config.shuffle:
        shuffle_presets(presets)

    playlist = Playlist(presets, loop=config.loop)

    # Compute socket path and check for stale socket
    try:
        socket_path = compute_socket_path()
    except RuntimeError as e:
        raise StartupError(str(e)) from None

    try:
        check_stale_socket(socket_path)
    except AlreadyRunningError as e:
        raise StartupError(str(e)) from None
    except StaleSocketError as e:
        raise StartupError(str(e)) from None

    # Check renderer binary exists
    try:
        find_renderer_binary()
    except RendererNotFoundError as e:
        raise StartupError(str(e)) from None

    # Run the async startup sequence
    asyncio.run(_async_main(
        socket_path=socket_path,
        audio_source=config.audio_source,
        playlist=playlist,
        preset_duration=config.preset_duration,
        fullscreen=config.fullscreen,
        output=output,
    ))
