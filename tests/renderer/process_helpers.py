#!/usr/bin/env python3
"""
Process management helpers for renderer tests.

Provides utilities for starting, connecting to, and managing renderer processes.
"""

import os
import socket
import subprocess

from renderer_helpers import wait_for_socket_ready


def start_renderer(socket_path: str) -> subprocess.Popen | None:
    """Start the renderer process.

    Args:
        socket_path: Path where the renderer should create its socket.

    Returns:
        The Popen object if successful, None if failed.
    """
    renderer_path = "build/platyplaty-renderer"
    if not os.path.exists(renderer_path):
        print(f"ERROR: Renderer not found at {renderer_path}")
        return None

    proc = subprocess.Popen(
        [renderer_path, "--socket-path", socket_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if not wait_for_socket_ready(proc):
        proc.kill()
        proc.wait()
        print("ERROR: Renderer did not print SOCKET READY")
        return None

    return proc


def connect_to_renderer(socket_path: str) -> socket.socket | None:
    """Connect to the renderer's Unix socket.

    Args:
        socket_path: Path to the renderer's socket.

    Returns:
        Connected socket if successful, None if failed.
    """
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.connect(socket_path)
        sock.settimeout(5.0)
        return sock
    except Exception as e:
        print(f"  Failed to connect: {e}")
        sock.close()
        return None


def cleanup_socket(path: str) -> None:
    """Remove socket file if it exists."""
    if os.path.exists(path):
        os.unlink(path)
