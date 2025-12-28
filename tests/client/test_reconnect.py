#!/usr/bin/env python3
"""
Unit tests for reconnect logic.

Tests the _sync_state_from_status function which uses GET STATUS to
synchronize client state with the renderer, skipping redundant commands.
"""

import io
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.playlist import Playlist
from platyplaty.reconnect import _sync_state_from_status
from platyplaty.socket_client import RendererError
from platyplaty.types import CommandResponse, StatusData


def make_status_response(
    audio_source: str = "@DEFAULT_SINK@.monitor",
    audio_connected: bool = True,
    preset_path: str = "",
    visible: bool = True,
    fullscreen: bool = False,
) -> CommandResponse:
    """Create a mock GET STATUS response."""
    return CommandResponse(
        id=1,
        success=True,
        data={
            "audio_source": audio_source,
            "audio_connected": audio_connected,
            "preset_path": preset_path,
            "visible": visible,
            "fullscreen": fullscreen,
        },
    )


@pytest.fixture
def mock_client() -> AsyncMock:
    """Create a mock SocketClient."""
    return AsyncMock()


@pytest.fixture
def playlist() -> Playlist:
    """Create a test playlist with a single preset."""
    return Playlist([Path("/presets/test.milk")])


@pytest.fixture
def output() -> io.StringIO:
    """Create a string buffer for output."""
    return io.StringIO()


@pytest.mark.asyncio
async def test_get_status_parses_response_into_statusdata(
    mock_client: AsyncMock,
    playlist: Playlist,
    output: io.StringIO,
) -> None:
    """send_command("GET STATUS") response parses correctly into StatusData."""
    mock_client.send_command.return_value = make_status_response(
        audio_source="test.monitor",
        audio_connected=True,
        preset_path="/presets/test.milk",
        visible=True,
        fullscreen=False,
    )
    result = await _sync_state_from_status(
        mock_client, playlist, fullscreen=False, output=output
    )
    assert result is True
    mock_client.send_command.assert_any_call("GET STATUS")
    call_args = mock_client.send_command.call_args_list[0]
    assert call_args[0][0] == "GET STATUS"


@pytest.mark.asyncio
async def test_reconnect_skips_redundant_commands_when_state_matches(
    mock_client: AsyncMock,
    playlist: Playlist,
    output: io.StringIO,
) -> None:
    """Reconnect skips LOAD PRESET, SHOW WINDOW, SET FULLSCREEN when state matches."""
    mock_client.send_command.return_value = make_status_response(
        preset_path=str(playlist.current()),
        visible=True,
        fullscreen=False,
    )
    result = await _sync_state_from_status(
        mock_client, playlist, fullscreen=False, output=output
    )
    assert result is True
    assert mock_client.send_command.call_count == 1
    mock_client.send_command.assert_called_once_with("GET STATUS")


@pytest.mark.asyncio
async def test_reconnect_sends_load_preset_when_preset_differs(
    mock_client: AsyncMock,
    playlist: Playlist,
    output: io.StringIO,
) -> None:
    """Reconnect sends LOAD PRESET only if preset differs from current."""
    status_response = make_status_response(
        preset_path="/other/preset.milk",
        visible=True,
        fullscreen=False,
    )
    load_response = CommandResponse(id=2, success=True)
    mock_client.send_command.side_effect = [status_response, load_response]
    result = await _sync_state_from_status(
        mock_client, playlist, fullscreen=False, output=output
    )
    assert result is True
    assert mock_client.send_command.call_count == 2
    calls = mock_client.send_command.call_args_list
    assert calls[0][0][0] == "GET STATUS"
    assert calls[1][0][0] == "LOAD PRESET"
    assert calls[1][1]["path"] == str(playlist.current())


@pytest.mark.asyncio
async def test_reconnect_sends_show_window_when_not_visible(
    mock_client: AsyncMock,
    playlist: Playlist,
    output: io.StringIO,
) -> None:
    """Reconnect sends SHOW WINDOW when visible is false."""
    status_response = make_status_response(
        preset_path=str(playlist.current()),
        visible=False,
        fullscreen=False,
    )
    show_response = CommandResponse(id=2, success=True)
    mock_client.send_command.side_effect = [status_response, show_response]
    result = await _sync_state_from_status(
        mock_client, playlist, fullscreen=False, output=output
    )
    assert result is True
    assert mock_client.send_command.call_count == 2
    calls = mock_client.send_command.call_args_list
    assert calls[0][0][0] == "GET STATUS"
    assert calls[1][0][0] == "SHOW WINDOW"


@pytest.mark.asyncio
async def test_reconnect_sends_set_fullscreen_when_differs(
    mock_client: AsyncMock,
    playlist: Playlist,
    output: io.StringIO,
) -> None:
    """Reconnect sends SET FULLSCREEN when fullscreen state differs."""
    status_response = make_status_response(
        preset_path=str(playlist.current()),
        visible=True,
        fullscreen=False,
    )
    fs_response = CommandResponse(id=2, success=True)
    mock_client.send_command.side_effect = [status_response, fs_response]
    result = await _sync_state_from_status(
        mock_client, playlist, fullscreen=True, output=output
    )
    assert result is True
    assert mock_client.send_command.call_count == 2
    calls = mock_client.send_command.call_args_list
    assert calls[0][0][0] == "GET STATUS"
    assert calls[1][0][0] == "SET FULLSCREEN"
    assert calls[1][1]["enabled"] is True


@pytest.mark.asyncio
async def test_reconnect_returns_false_on_get_status_failure(
    mock_client: AsyncMock,
    playlist: Playlist,
    output: io.StringIO,
) -> None:
    """Reconnect returns False if GET STATUS fails."""
    mock_client.send_command.side_effect = RendererError("error", 1)
    result = await _sync_state_from_status(
        mock_client, playlist, fullscreen=False, output=output
    )
    assert result is False


@pytest.mark.asyncio
async def test_reconnect_warns_on_audio_disconnected(
    mock_client: AsyncMock,
    playlist: Playlist,
    output: io.StringIO,
) -> None:
    """Reconnect warns but continues when audio_connected is false."""
    mock_client.send_command.return_value = make_status_response(
        audio_connected=False,
        preset_path=str(playlist.current()),
        visible=True,
        fullscreen=False,
    )
    result = await _sync_state_from_status(
        mock_client, playlist, fullscreen=False, output=output
    )
    assert result is True
    assert "Audio disconnected" in output.getvalue()
