#!/usr/bin/env python3
"""Startup sequence execution for Platyplaty.

This module contains the functions for running the startup sequence
after configuration has been loaded and validated.
"""

import asyncio
from pathlib import Path
from typing import TextIO

from platyplaty.async_main import async_main
from platyplaty.errors import StartupError
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
)
from platyplaty.socket_path import (
    AlreadyRunningError,
    StaleSocketError,
    check_stale_socket,
    compute_socket_path,
)
from platyplaty.types import Config


def expand_preset_dirs(preset_dirs: list[str]) -> list[str]:
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


def validate_preset_dirs(preset_dirs: list[str]) -> None:
    """Validate that all preset directories exist.

    Args:
        preset_dirs: List of absolute directory paths.

    Raises:
        StartupError: If any directory does not exist.
    """
    for path in preset_dirs:
        if not Path(path).is_dir():
            raise StartupError(f"Preset directory not found: {path}")


def run_startup_sequence(config: Config, output: TextIO) -> None:
    """Run the main startup sequence.

    Args:
        config: Validated configuration.
        output: Output stream for status messages.

    Raises:
        StartupError: If any startup step fails.
    """
    # Expand and resolve preset directory paths
    preset_dirs = expand_preset_dirs(config.preset_dirs)
    validate_preset_dirs(preset_dirs)

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
    asyncio.run(async_main(
        socket_path=socket_path,
        audio_source=config.audio_source,
        playlist=playlist,
        preset_duration=config.preset_duration,
        fullscreen=config.fullscreen,
        output=output,
    ))
