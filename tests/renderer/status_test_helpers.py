#!/usr/bin/env python3
"""
Helper functions for GET STATUS integration tests.

Provides socket connection setup and renderer initialization utilities.
"""

import socket

from renderer_helpers import send_command


def create_connected_socket(socket_path: str) -> socket.socket:
    """Create a connected socket with timeout configured."""
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(socket_path)
    sock.settimeout(5.0)
    return sock


def init_renderer(
    sock: socket.socket,
    audio_source: str = "@DEFAULT_SINK@.monitor"
) -> None:
    """Initialize renderer with CHANGE AUDIO SOURCE and INIT commands."""
    resp = send_command(sock, {
        "command": "CHANGE AUDIO SOURCE",
        "id": 1,
        "audio_source": audio_source
    })
    assert resp.get("success"), f"CHANGE AUDIO SOURCE failed: {resp}"
    resp = send_command(sock, {"command": "INIT", "id": 2})
    assert resp.get("success"), f"INIT failed: {resp}"
