#!/usr/bin/env python3
"""Startup sequence execution for Platyplaty.

This module contains the functions for running the startup sequence
after configuration has been loaded and validated.
"""

from pathlib import Path

from platyplaty.app import PlatyplatyApp
from platyplaty.errors import InaccessibleDirectoryError, StartupError
from platyplaty.path_resolution import resolve_path_argument
from platyplaty.playlist import Playlist
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


def run_startup_sequence(config: Config, path_argument: str | None) -> None:
    """Run the main startup sequence.

    Args:
        config: Validated configuration.
        path_argument: Optional path to directory or .platy playlist file.

    Raises:
        StartupError: If any startup step fails.
    """
    # Resolve path argument to start directory and playlist path
    resolved = resolve_path_argument(path_argument)

    # Determine effective playlist path (path argument overrides config)
    effective_playlist_path = resolved.playlist_path
    if effective_playlist_path is None and config.playlist:
        effective_playlist_path = Path(config.playlist)
    playlist = _create_playlist(effective_playlist_path)

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
        audio_source=config.renderer.audio_source,
        preset_duration=config.keybindings.playlist.preset_duration,
        fullscreen=config.renderer.fullscreen,
        keybindings=config.keybindings,
    )

    # Create and run Textual app
    app = PlatyplatyApp(
        config=app_config,
        playlist=playlist,
        start_path=resolved.start_directory,
    )
    try:
        app.run()
    except InaccessibleDirectoryError as e:
        raise StartupError(str(e)) from None


def _create_playlist(playlist_path: Path | None) -> Playlist:
    """Create playlist from path or return empty playlist.

    Args:
        playlist_path: Path to .platy playlist file, or None.

    Returns:
        Playlist loaded from file, or empty playlist if no path given.

    Raises:
        StartupError: If playlist file cannot be loaded.
    """
    playlist = Playlist(presets=[], loop=True)
    if playlist_path is not None:
        try:
            playlist.load_from_file(playlist_path)
        except Exception as e:
            raise StartupError(f"Could not load playlist: {e}") from None
    return playlist

