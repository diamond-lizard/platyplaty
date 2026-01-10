#!/usr/bin/env python3
"""
Integration tests for Stage 2 renderer functionality.

Tests the happy path: connect to socket, send commands, verify responses.
"""

import os
import socket
import subprocess
import tempfile
import time

import pytest

from renderer_helpers import send_command, wait_for_socket_ready


@pytest.fixture
def socket_path() -> str:
    """Create a temporary socket path."""
    path = os.path.join(tempfile.gettempdir(), f"platyplaty-test-{os.getpid()}.sock")
    if os.path.exists(path):
        os.unlink(path)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def renderer_path() -> str:
    """Get the renderer binary path."""
    path = "build/platyplaty-renderer"
    if not os.path.exists(path):
        pytest.skip("Renderer not built. Run 'make' first.")
    return path


def test_happy_path(socket_path: str, renderer_path: str) -> None:
    """Test the complete Stage 2 initialization sequence."""
    proc = subprocess.Popen(
        [renderer_path, "--socket-path", socket_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    try:
        _run_happy_path_test(proc, socket_path)
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait()


def _run_happy_path_test(proc: subprocess.Popen, socket_path: str) -> None:
    """Execute the happy path test sequence."""
    assert wait_for_socket_ready(proc), "No SOCKET READY"
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(socket_path)
    sock.settimeout(5.0)
    _send_init_sequence(sock)
    _send_preset_and_show(sock)
    _send_quit_and_verify(sock, proc)


def _send_init_sequence(sock: socket.socket) -> None:
    """Send CHANGE AUDIO SOURCE and INIT commands."""
    resp = send_command(sock, {
        "command": "CHANGE AUDIO SOURCE",
        "id": 1,
        "audio_source": "@DEFAULT_SINK@.monitor"
    })
    assert resp.get("success"), f"CHANGE AUDIO SOURCE failed: {resp}"
    resp = send_command(sock, {"command": "INIT", "id": 2})
    assert resp.get("success"), f"INIT failed: {resp}"


def _send_preset_and_show(sock: socket.socket) -> None:
    """Send LOAD PRESET and SHOW WINDOW commands."""
    preset = "presets/test/101-per_frame.milk"
    if os.path.exists(preset):
        resp = send_command(sock, {
            "command": "LOAD PRESET",
            "id": 3,
            "path": os.path.abspath(preset)
        })
        assert resp.get("success"), f"LOAD PRESET failed: {resp}"
    resp = send_command(sock, {"command": "SHOW WINDOW", "id": 4})
    assert resp.get("success"), f"SHOW WINDOW failed: {resp}"


def _send_quit_and_verify(sock: socket.socket, proc: subprocess.Popen) -> None:
    """Send QUIT command and verify clean exit."""
    time.sleep(0.5)
    resp = send_command(sock, {"command": "QUIT", "id": 5})
    assert resp.get("success"), f"QUIT failed: {resp}"
    sock.close()
    exit_code = proc.wait(timeout=5)
    assert exit_code == 0, f"Renderer exited with code {exit_code}"
