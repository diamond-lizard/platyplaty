#!/usr/bin/env python3
"""
GET STATUS window state integration tests.

Tests that visible and fullscreen fields accurately reflect window state.
"""

import pytest

from renderer_helpers import send_command
from status_test_helpers import create_connected_socket, init_renderer


def test_visible_reflects_show_window(
    socket_path: str, renderer_process, renderer_path: str
) -> None:
    """visible reflects SHOW WINDOW state (false initially, true after)."""
    sock = create_connected_socket(socket_path)
    init_renderer(sock)
    resp = send_command(sock, {"command": "GET STATUS", "id": 10})
    assert resp.get("success"), f"GET STATUS failed: {resp}"
    assert resp["data"]["visible"] is False, "visible should be False initially"
    resp = send_command(sock, {"command": "SHOW WINDOW", "id": 11})
    assert resp.get("success"), f"SHOW WINDOW failed: {resp}"
    resp = send_command(sock, {"command": "GET STATUS", "id": 12})
    assert resp.get("success"), f"GET STATUS failed: {resp}"
    assert resp["data"]["visible"] is True, "visible should be True after SHOW WINDOW"
    sock.close()


def test_fullscreen_reflects_set_fullscreen(
    socket_path: str, renderer_process, renderer_path: str
) -> None:
    """fullscreen reflects SET FULLSCREEN state."""
    sock = create_connected_socket(socket_path)
    init_renderer(sock)
    resp = send_command(sock, {"command": "SHOW WINDOW", "id": 10})
    assert resp.get("success"), f"SHOW WINDOW failed: {resp}"
    resp = send_command(sock, {"command": "GET STATUS", "id": 11})
    assert resp.get("success"), f"GET STATUS failed: {resp}"
    assert resp["data"]["fullscreen"] is False, "fullscreen should be False initially"
    resp = send_command(sock, {
        "command": "SET FULLSCREEN",
        "id": 12,
        "enabled": True
    })
    assert resp.get("success"), f"SET FULLSCREEN failed: {resp}"
    resp = send_command(sock, {"command": "GET STATUS", "id": 13})
    assert resp.get("success"), f"GET STATUS failed: {resp}"
    assert resp["data"]["fullscreen"] is True, "fullscreen should be True"
    resp = send_command(sock, {
        "command": "SET FULLSCREEN",
        "id": 14,
        "enabled": False
    })
    assert resp.get("success"), f"SET FULLSCREEN failed: {resp}"
    resp = send_command(sock, {"command": "GET STATUS", "id": 15})
    assert resp.get("success"), f"GET STATUS failed: {resp}"
    assert resp["data"]["fullscreen"] is False, "fullscreen should be False again"
    sock.close()
