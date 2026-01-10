#!/usr/bin/env python3
"""
Integration tests for GET STATUS command.

Tests the GET STATUS command behavior before and after INIT, and verifies
that returned fields accurately reflect renderer state.
"""

import os
import socket

import pytest

from renderer_helpers import send_command


def test_get_status_before_init(
    socket_path: str, renderer_process, renderer_path: str
) -> None:
    """GET STATUS before INIT returns error."""
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(socket_path)
    sock.settimeout(5.0)
    resp = send_command(sock, {"command": "GET STATUS", "id": 1})
    assert not resp.get("success"), "GET STATUS should fail before INIT"
    assert "command not allowed before INIT" in resp.get("error", "")
    sock.close()


def test_get_status_after_init_has_all_fields(
    socket_path: str, renderer_process, renderer_path: str
) -> None:
    """GET STATUS after INIT returns success with all 5 fields present."""
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(socket_path)
    sock.settimeout(5.0)
    _init_renderer(sock)
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
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(socket_path)
    sock.settimeout(5.0)
    audio_source = "@DEFAULT_SINK@.monitor"
    _init_renderer(sock, audio_source=audio_source)
    resp = send_command(sock, {"command": "GET STATUS", "id": 10})
    assert resp.get("success"), f"GET STATUS failed: {resp}"
    assert resp["data"]["audio_source"] == audio_source
    sock.close()


def test_preset_path_empty_before_load(
    socket_path: str, renderer_process, renderer_path: str
) -> None:
    """preset_path is empty string before any LOAD PRESET."""
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(socket_path)
    sock.settimeout(5.0)
    _init_renderer(sock)
    resp = send_command(sock, {"command": "GET STATUS", "id": 10})
    assert resp.get("success"), f"GET STATUS failed: {resp}"
    assert resp["data"]["preset_path"] == ""
    sock.close()


def test_preset_path_matches_load_preset(
    socket_path: str, renderer_process, renderer_path: str
) -> None:
    """preset_path matches last successful LOAD PRESET path."""
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(socket_path)
    sock.settimeout(5.0)
    _init_renderer(sock)
    preset = os.path.abspath("presets/test/101-per_frame.milk")
    resp = send_command(sock, {
        "command": "LOAD PRESET",
        "id": 10,
        "path": preset
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
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(socket_path)
    sock.settimeout(5.0)
    _init_renderer(sock)
    good_preset = os.path.abspath("presets/test/101-per_frame.milk")
    resp = send_command(sock, {
        "command": "LOAD PRESET",
        "id": 10,
        "path": good_preset
    })
    assert resp.get("success"), f"LOAD PRESET failed: {resp}"
    bad_preset = "/nonexistent/path/to/preset.milk"
    resp = send_command(sock, {
        "command": "LOAD PRESET",
        "id": 11,
        "path": bad_preset
    })
    assert not resp.get("success"), "LOAD PRESET should fail for bad path"
    resp = send_command(sock, {"command": "GET STATUS", "id": 12})
    assert resp.get("success"), f"GET STATUS failed: {resp}"
    assert resp["data"]["preset_path"] == good_preset
    sock.close()


def test_visible_reflects_show_window(
    socket_path: str, renderer_process, renderer_path: str
) -> None:
    """visible reflects SHOW WINDOW state (false initially, true after)."""
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(socket_path)
    sock.settimeout(5.0)
    _init_renderer(sock)
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
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(socket_path)
    sock.settimeout(5.0)
    _init_renderer(sock)
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


def _init_renderer(
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
