#!/usr/bin/env python3
"""
Helper functions for renderer integration tests.

Provides netstring encoding/decoding and command sending utilities.
"""

import json
import socket
import subprocess
import time


def encode_netstring(payload: str) -> bytes:
    """Encode a string as a netstring."""
    encoded = payload.encode('utf-8')
    return f"{len(encoded)}:{payload},".encode('utf-8')


def decode_netstring(data: bytes) -> tuple[str | None, int]:
    """Decode a netstring, return (payload, bytes_consumed) or (None, 0)."""
    try:
        text = data.decode('utf-8')
        colon_idx = text.index(':')
        length = int(text[:colon_idx])
        start = colon_idx + 1
        end = start + length
        if len(text) < end + 1 or text[end] != ',':
            return None, 0
        return text[start:end], end + 1
    except (ValueError, IndexError):
        return None, 0


def send_command(sock: socket.socket, cmd: dict) -> dict:
    """Send a command and receive the response."""
    payload = json.dumps(cmd)
    sock.sendall(encode_netstring(payload))
    return _receive_response(sock)


def _receive_response(sock: socket.socket) -> dict:
    """Receive and decode a netstring response."""
    response_data = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            raise ConnectionError("Connection closed by renderer")
        response_data += chunk
        decoded, _ = decode_netstring(response_data)
        if decoded is not None:
            return json.loads(decoded)


def wait_for_socket_ready(proc: subprocess.Popen, timeout: float = 5.0) -> bool:
    """Wait for SOCKET READY message on stdout."""
    import select
    start = time.time()
    while time.time() - start < timeout:
        if proc.poll() is not None:
            return False
        ready, _, _ = select.select([proc.stdout], [], [], 0.1)
        if not ready:
            continue
        line = proc.stdout.readline() if proc.stdout else ""
        if line.strip() == "SOCKET READY":
            return True
    return False
