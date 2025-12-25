#!/usr/bin/env python3
"""
Shared pytest fixtures for renderer integration tests.

Provides socket path computation and renderer process management.
"""

import os
import subprocess
import tempfile
from collections.abc import Generator

import pytest

from helpers import wait_for_socket_ready


@pytest.fixture
def socket_path() -> Generator[str, None, None]:
    """Create a temporary socket path, clean up after test."""
    path = os.path.join(
        tempfile.gettempdir(), f"platyplaty-test-{os.getpid()}.sock"
    )
    if os.path.exists(path):
        os.unlink(path)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def renderer_path() -> str:
    """Get the renderer binary path, skip if not built."""
    path = "build/platyplaty-renderer"
    if not os.path.exists(path):
        pytest.skip("Renderer not built. Run 'make' first.")
    return path


@pytest.fixture
def renderer_process(
    socket_path: str, renderer_path: str
) -> Generator[subprocess.Popen, None, None]:
    """Start renderer and wait for SOCKET READY, cleanup on exit."""
    proc = subprocess.Popen(
        [renderer_path, "--socket-path", socket_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if not wait_for_socket_ready(proc):
        proc.kill()
        proc.wait()
        pytest.fail("Renderer did not emit SOCKET READY")
    yield proc
    if proc.poll() is None:
        proc.kill()
        proc.wait()
