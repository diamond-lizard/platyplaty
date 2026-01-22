#!/usr/bin/env python3
"""
Test client disconnect behavior.

Tests that the renderer exits cleanly when client disconnects (prevents orphaned processes).
"""

import subprocess
import time

from process_helpers import cleanup_socket, connect_to_renderer, start_renderer
from shutdown_helpers import ShutdownResult, init_renderer


def run_client_disconnect_test(socket_path: str) -> ShutdownResult:
    """Test that renderer exits cleanly when client disconnects."""
    print("\n=== Test: Client disconnect (renderer should exit cleanly) ===")

    proc = start_renderer(socket_path)
    if not proc:
        return ShutdownResult("Client disconnect", False, "Failed to start renderer")

    sock = connect_to_renderer(socket_path)
    if not sock:
        proc.kill()
        proc.wait()
        return ShutdownResult("Client disconnect", False, "Failed to connect")

    cmd_id = [1]
    if not init_renderer(sock, cmd_id):
        sock.close()
        proc.kill()
        proc.wait()
        return ShutdownResult("Client disconnect", False, "Failed to initialize")

    print("  Disconnecting client...")
    sock.close()
    time.sleep(1.0)


    try:
        exit_code = proc.wait(timeout=5.0)
        if exit_code == 0:
            return ShutdownResult("Client disconnect", True, "Renderer exited cleanly")
        return ShutdownResult("Client disconnect", False, f"Exit code {exit_code}")
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        return ShutdownResult("Client disconnect", False, "Renderer did not exit")

def test_client_disconnect(socket_path: str) -> None:
    """Pytest wrapper for client disconnect test."""
    cleanup_socket(socket_path)
    result = run_client_disconnect_test(socket_path)
    assert result.passed, result.details
