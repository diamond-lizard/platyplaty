#!/usr/bin/env python3
"""
Tests for transition_type field in LOAD PRESET commands.

Verifies that the renderer correctly accepts "soft" and "hard"
transition types, and rejects missing or invalid values.
"""

from renderer_helpers import send_command
from status_test_helpers import create_connected_socket, init_renderer


def test_load_preset_soft_transition(
    socket_path: str, renderer_process, renderer_path: str
) -> None:
    """LOAD PRESET with transition_type="soft" succeeds."""
    sock = create_connected_socket(socket_path)
    init_renderer(sock)
    resp = send_command(sock, {
        "command": "LOAD PRESET",
        "id": 10,
        "path": "idle://",
        "transition_type": "soft"
    })
    assert resp.get("success"), f"LOAD PRESET soft failed: {resp}"
    sock.close()


def test_load_preset_hard_transition(
    socket_path: str, renderer_process, renderer_path: str
) -> None:
    """LOAD PRESET with transition_type="hard" succeeds."""
    sock = create_connected_socket(socket_path)
    init_renderer(sock)
    resp = send_command(sock, {
        "command": "LOAD PRESET",
        "id": 10,
        "path": "idle://",
        "transition_type": "hard"
    })
    assert resp.get("success"), f"LOAD PRESET hard failed: {resp}"
    sock.close()


def test_load_preset_missing_transition_type(
    socket_path: str, renderer_process, renderer_path: str
) -> None:
    """LOAD PRESET without transition_type field returns error."""
    sock = create_connected_socket(socket_path)
    init_renderer(sock)
    resp = send_command(sock, {
        "command": "LOAD PRESET",
        "id": 10,
        "path": "idle://"
    })
    assert not resp.get("success"), "should fail without transition_type"
    assert "transition_type" in resp.get("error", "")
    sock.close()


def test_load_preset_invalid_transition_type(
    socket_path: str, renderer_process, renderer_path: str
) -> None:
    """LOAD PRESET with invalid transition_type returns error."""
    sock = create_connected_socket(socket_path)
    init_renderer(sock)
    resp = send_command(sock, {
        "command": "LOAD PRESET",
        "id": 10,
        "path": "idle://",
        "transition_type": "invalid"
    })
    assert not resp.get("success"), "should fail with invalid transition_type"
    assert "transition_type" in resp.get("error", "")
    sock.close()
