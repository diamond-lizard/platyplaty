#!/usr/bin/env python3
"""Unit tests for run_startup_sequence start_path passing."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

PATCH_BASE = "platyplaty.run_sequence"


def _make_config() -> MagicMock:
    """Create a mock Config for testing."""
    from platyplaty.types import Config
    config = MagicMock(spec=Config)
    config.playlist = None
    config.renderer.audio_source = "pulse"
    config.renderer.fullscreen = False
    config.keybindings.playlist.preset_duration = 30
    return config


@patch(f"{PATCH_BASE}.compute_socket_path")
@patch(f"{PATCH_BASE}.check_stale_socket")
@patch(f"{PATCH_BASE}.find_renderer_binary")
@patch(f"{PATCH_BASE}.PlatyplatyApp")
def test_directory_arg_passes_start_path(
    mock_app: MagicMock, _rb: MagicMock, _ss: MagicMock, _sp: MagicMock,
    tmp_path: Path,
) -> None:
    """Directory argument should pass start_path to app."""
    from platyplaty.run_sequence import run_startup_sequence
    test_dir = tmp_path / "presets"
    test_dir.mkdir()
    mock_app.return_value.run.return_value = None
    run_startup_sequence(_make_config(), str(test_dir))
    assert mock_app.call_args.kwargs["start_path"] == test_dir


@patch(f"{PATCH_BASE}.compute_socket_path")
@patch(f"{PATCH_BASE}.check_stale_socket")
@patch(f"{PATCH_BASE}.find_renderer_binary")
@patch(f"{PATCH_BASE}.PlatyplatyApp")
def test_playlist_arg_passes_parent_as_start_path(
    mock_app: MagicMock, _rb: MagicMock, _ss: MagicMock, _sp: MagicMock,
    tmp_path: Path,
) -> None:
    """Playlist argument should pass parent dir as start_path."""
    from platyplaty.run_sequence import run_startup_sequence
    playlist_file = tmp_path / "test.platy"
    playlist_file.write_text("")
    mock_app.return_value.run.return_value = None
    run_startup_sequence(_make_config(), str(playlist_file))
    assert mock_app.call_args.kwargs["start_path"] == tmp_path


@patch(f"{PATCH_BASE}.compute_socket_path")
@patch(f"{PATCH_BASE}.check_stale_socket")
@patch(f"{PATCH_BASE}.find_renderer_binary")
@patch(f"{PATCH_BASE}.PlatyplatyApp")
def test_no_arg_passes_cwd_as_start_path(
    mock_app: MagicMock, _rb: MagicMock, _ss: MagicMock, _sp: MagicMock,
) -> None:
    """No path argument should pass cwd as start_path."""
    from platyplaty.run_sequence import run_startup_sequence
    mock_app.return_value.run.return_value = None
    run_startup_sequence(_make_config(), None)
    assert mock_app.call_args.kwargs["start_path"] == Path.cwd()
