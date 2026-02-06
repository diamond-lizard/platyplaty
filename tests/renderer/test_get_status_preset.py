#!/usr/bin/env python3
"""
GET STATUS preset_path field integration tests.

Tests that preset_path accurately reflects loaded presets.
"""

import os

import pytest

from renderer_helpers import send_command
from status_test_helpers import create_connected_socket, init_renderer


def test_preset_path_empty_before_load(
    socket_path: str, renderer_process, renderer_path: str
) -> None:
    """preset_path is empty string before any LOAD PRESET."""
    sock = create_connected_socket(socket_path)
    init_renderer(sock)
    resp = send_command(sock, {"command": "GET STATUS", "id": 10})
    assert resp.get("success"), f"GET STATUS failed: {resp}"
    assert resp["data"]["preset_path"] == ""
    sock.close()


def test_preset_path_matches_load_preset(
    socket_path: str, renderer_process, renderer_path: str
) -> None:
    """preset_path matches last successful LOAD PRESET path."""
    sock = create_connected_socket(socket_path)
    init_renderer(sock)
    preset = os.path.abspath("presets/test/101-per_frame.milk")
    resp = send_command(sock, {
        "command": "LOAD PRESET",
        "id": 10,
        "path": preset,
        "transition_type": "hard"
    })
    assert resp.get("success"), f"LOAD PRESET failed: {resp}"
    resp = send_command(sock, {"command": "GET STATUS", "id": 11})
    assert resp.get("success"), f"GET STATUS failed: {resp}"
    assert resp["data"]["preset_path"] == preset
    sock.close()


def test_preset_path_unchanged_after_failed_load(
    socket_path: str, renderer_process, renderer_path: str
) -> None:
    """preset_path remains unchanged after a failed LOAD PRESET."""
    sock = create_connected_socket(socket_path)
    init_renderer(sock)
    good_preset = os.path.abspath("presets/test/101-per_frame.milk")
    resp = send_command(sock, {
        "command": "LOAD PRESET",
        "id": 10,
        "path": good_preset,
        "transition_type": "hard"
    })
    assert resp.get("success"), f"LOAD PRESET failed: {resp}"
    bad_preset = "/nonexistent/path/to/preset.milk"
    resp = send_command(sock, {
        "command": "LOAD PRESET",
        "id": 11,
        "path": bad_preset,
        "transition_type": "hard"
    })
    assert not resp.get("success"), "LOAD PRESET should fail for bad path"
    resp = send_command(sock, {"command": "GET STATUS", "id": 12})
    assert resp.get("success"), f"GET STATUS failed: {resp}"
    assert resp["data"]["preset_path"] == good_preset
    sock.close()
