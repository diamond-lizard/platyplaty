#!/usr/bin/env python3
"""Startup sequence execution for Platyplaty.

This module contains the functions for running the startup sequence
after configuration has been loaded and validated.
"""

from platyplaty.app import PlatyplatyApp
from platyplaty.errors import InaccessibleDirectoryError, StartupError
from platyplaty.playlist import Playlist
from platyplaty.preset_dirs import expand_preset_dirs, validate_preset_dirs
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
from platyplaty.types.app_config import AppConfig


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

    # Create AppConfig with computed socket_path and config values
    app_config = AppConfig(
        socket_path=socket_path,
        audio_source=config.audio_source,
        preset_duration=config.preset_duration,
        fullscreen=config.fullscreen,
        keybindings=config.keybindings,
    )

    # Create and run Textual app
    app = PlatyplatyApp(config=app_config, playlist=playlist)
    try:
        app.run()
    except InaccessibleDirectoryError as e:
        raise StartupError(str(e)) from None
