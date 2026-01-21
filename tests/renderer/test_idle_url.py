#!/usr/bin/env python3
"""
Tests for idle:// URL handling in the renderer.

The idle:// URL is a special pseudo-preset that displays nothing.
It skips file validation and returns success without loading any preset.
"""

import os

import pytest

from renderer_helpers import send_command
from status_test_helpers import create_connected_socket, init_renderer


def test_idle_url_load_succeeds(
    socket_path: str, renderer_process, renderer_path: str
) -> None:
    """LOAD PRESET with idle:// URL succeeds."""
    sock = create_connected_socket(socket_path)
    init_renderer(sock)
    resp = send_command(sock, {
        "command": "LOAD PRESET",
        "id": 10,
        "path": "idle://"
    })
    assert resp.get("success"), f"LOAD PRESET idle:// failed: {resp}"
    sock.close()


def test_idle_url_sets_preset_path(
    socket_path: str, renderer_process, renderer_path: str
) -> None:
    """GET STATUS shows idle:// as preset_path after loading."""
    sock = create_connected_socket(socket_path)
    init_renderer(sock)
    send_command(sock, {
        "command": "LOAD PRESET",
        "id": 10,
        "path": "idle://"
    })
    resp = send_command(sock, {"command": "GET STATUS", "id": 11})
    assert resp.get("success"), f"GET STATUS failed: {resp}"
    assert resp["data"]["preset_path"] == "idle://"
    sock.close()


def test_idle_url_after_real_preset(
    socket_path: str, renderer_process, renderer_path: str
) -> None:
    """Loading idle:// after a real preset updates preset_path."""
    sock = create_connected_socket(socket_path)
    init_renderer(sock)
    preset = os.path.abspath("presets/test/101-per_frame.milk")
    send_command(sock, {
        "command": "LOAD PRESET",
        "id": 10,
        "path": preset
    })
    send_command(sock, {
        "command": "LOAD PRESET",
        "id": 11,
        "path": "idle://"
    })
    resp = send_command(sock, {"command": "GET STATUS", "id": 12})
    assert resp.get("success"), f"GET STATUS failed: {resp}"
    assert resp["data"]["preset_path"] == "idle://"
    sock.close()
