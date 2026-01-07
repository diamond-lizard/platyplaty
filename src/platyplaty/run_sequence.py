#!/usr/bin/env python3
"""Startup sequence execution for Platyplaty.

This module contains the functions for running the startup sequence
after configuration has been loaded and validated.
"""

from pathlib import Path

from platyplaty.app import PlatyplatyApp
from platyplaty.errors import InaccessibleDirectoryError, StartupError
from platyplaty.paths import UndefinedEnvVarError, expand_path, resolve_path
from platyplaty.playlist import Playlist
from platyplaty.preset_scanner import (
    NoPresetsFoundError,
    scan_preset_dirs,
    shuffle_presets,
)
from platyplaty.renderer_binary import (
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


def run_startup_sequence(config: Config) -> None:
    """Run the main startup sequence.

    Args:
        config: Validated configuration.

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

    # Create and run Textual app
    app = PlatyplatyApp(
        socket_path=socket_path,
        audio_source=config.audio_source,
        playlist=playlist,
        preset_duration=config.preset_duration,
        fullscreen=config.fullscreen,
        client_keybindings=config.keybindings.client,
        renderer_keybindings=config.keybindings.renderer,
        file_browser_keybindings=config.keybindings.file_browser,
    )
    try:
        app.run()
    except InaccessibleDirectoryError as e:
        raise StartupError(str(e)) from None
