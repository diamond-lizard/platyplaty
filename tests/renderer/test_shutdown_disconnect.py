#!/usr/bin/env python3
"""
Test client disconnect behavior.

Tests that the renderer stays alive after client disconnect and accepts new clients.
"""

import subprocess
import time

from process_helpers import cleanup_socket, connect_to_renderer, start_renderer
from renderer_helpers import send_command
from shutdown_helpers import ShutdownResult, init_renderer


def run_client_disconnect_test(socket_path: str) -> ShutdownResult:
    """Test that renderer stays alive after client disconnect."""
    print("\n=== Test: Client disconnect (renderer should stay alive) ===")

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

    if proc.poll() is not None:
        return ShutdownResult(
            "Client disconnect", False,
            f"Renderer exited unexpectedly with code {proc.returncode}"
        )

    return _try_reconnect(socket_path, proc)


def _try_reconnect(socket_path: str, proc: subprocess.Popen) -> ShutdownResult:
    """Try to reconnect after disconnect and send QUIT."""
    print("  Attempting to reconnect...")
    sock2 = connect_to_renderer(socket_path)
    if not sock2:
        proc.kill()
        proc.wait()
        return ShutdownResult("Client disconnect", False, "Could not reconnect")

    try:
        _ = send_command(sock2, {"command": "QUIT", "id": 1})
        sock2.close()
    except ConnectionError:
        sock2.close()
    except Exception as e:
        sock2.close()
        proc.kill()
        proc.wait()
        return ShutdownResult("Client disconnect", False, f"Error with new client: {e}")

    return _wait_for_exit(proc)


def _wait_for_exit(proc: subprocess.Popen) -> ShutdownResult:
    """Wait for renderer to exit after QUIT."""
    try:
        exit_code = proc.wait(timeout=5.0)
        if exit_code == 0:
            msg = "Renderer stayed alive and accepted new client"
            return ShutdownResult("Client disconnect", True, msg)
        else:
            return ShutdownResult("Client disconnect", False, f"Exit code {exit_code}")
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        return ShutdownResult("Client disconnect", False, "Renderer did not exit after QUIT")


def test_client_disconnect(socket_path: str) -> None:
    """Pytest wrapper for client disconnect test."""
    cleanup_socket(socket_path)
    result = run_client_disconnect_test(socket_path)
    assert result.passed, result.details
