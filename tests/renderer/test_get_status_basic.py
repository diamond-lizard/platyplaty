#!/usr/bin/env python3
"""
Basic GET STATUS integration tests.

Tests the GET STATUS command behavior before and after INIT, and verifies
audio source field accuracy.
"""

import pytest

from renderer_helpers import send_command
from status_test_helpers import create_connected_socket, init_renderer


def test_get_status_before_init(
    socket_path: str, renderer_process, renderer_path: str
) -> None:
    """GET STATUS before INIT returns error."""
    sock = create_connected_socket(socket_path)
    resp = send_command(sock, {"command": "GET STATUS", "id": 1})
    assert not resp.get("success"), "GET STATUS should fail before INIT"
    assert "command not allowed before INIT" in resp.get("error", "")
    sock.close()


def test_get_status_after_init_has_all_fields(
    socket_path: str, renderer_process, renderer_path: str
) -> None:
    """GET STATUS after INIT returns success with all 5 fields present."""
    sock = create_connected_socket(socket_path)
    init_renderer(sock)
    resp = send_command(sock, {"command": "GET STATUS", "id": 10})
    assert resp.get("success"), f"GET STATUS failed: {resp}"
    data = resp.get("data", {})
    assert "audio_source" in data, "Missing audio_source field"
    assert "audio_connected" in data, "Missing audio_connected field"
    assert "preset_path" in data, "Missing preset_path field"
    assert "visible" in data, "Missing visible field"
    assert "fullscreen" in data, "Missing fullscreen field"
    sock.close()


def test_audio_source_matches_change_audio_source(
    socket_path: str, renderer_process, renderer_path: str
) -> None:
    """audio_source matches value from CHANGE AUDIO SOURCE command."""
    sock = create_connected_socket(socket_path)
    audio_source = "@DEFAULT_SINK@.monitor"
    init_renderer(sock, audio_source=audio_source)
    resp = send_command(sock, {"command": "GET STATUS", "id": 10})
    assert resp.get("success"), f"GET STATUS failed: {resp}"
    assert resp["data"]["audio_source"] == audio_source
    sock.close()
