#!/usr/bin/env python3
"""
Error path tests for Stage 2 renderer functionality.

Tests error handling: missing audio source, unknown commands, malformed input.
"""

import socket

import pytest

from renderer_helpers import encode_netstring, decode_netstring, send_command


def test_init_without_audio_source(
    socket_path: str, renderer_process, renderer_path: str
) -> None:
    """INIT without prior CHANGE AUDIO SOURCE returns error."""
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(socket_path)
    sock.settimeout(5.0)
    resp = send_command(sock, {"command": "INIT", "id": 1})
    assert not resp.get("success"), "INIT should fail without audio source"
    assert "error" in resp
    sock.close()


def test_unknown_command(
    socket_path: str, renderer_process, renderer_path: str
) -> None:
    """Unknown command returns error response."""
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(socket_path)
    sock.settimeout(5.0)
    resp = send_command(sock, {"command": "BOGUS_COMMAND", "id": 1})
    assert not resp.get("success"), "Unknown command should fail"
    assert "error" in resp
    sock.close()


def test_malformed_json(
    socket_path: str, renderer_process, renderer_path: str
) -> None:
    """Malformed JSON returns error response."""
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(socket_path)
    sock.settimeout(5.0)
    malformed = encode_netstring("{not valid json")
    sock.sendall(malformed)
    response_data = sock.recv(4096)
    decoded, _ = decode_netstring(response_data)
    assert decoded is not None, "Should receive a response"
    import json
    resp = json.loads(decoded)
    assert not resp.get("success"), "Malformed JSON should fail"
    sock.close()


def test_invalid_netstring(
    socket_path: str, renderer_process, renderer_path: str
) -> None:
    """Invalid netstring causes disconnect (renderer stays alive)."""
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(socket_path)
    sock.settimeout(5.0)
    sock.sendall(b"999999:way too long,")
    try:
        data = sock.recv(4096)
        if not data:
            pass
    except (ConnectionError, socket.timeout):
        pass
    sock.close()
    assert renderer_process.poll() is None, "Renderer should stay alive"
