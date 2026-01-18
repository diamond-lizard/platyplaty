#!/usr/bin/env python3
"""
Test QUIT command shutdown path.

Tests that the QUIT command causes the renderer to exit cleanly.
"""

import subprocess

from process_helpers import cleanup_socket, connect_to_renderer, start_renderer
from renderer_helpers import send_command
from shutdown_helpers import ShutdownResult, init_renderer


def run_quit_command_test(socket_path: str) -> ShutdownResult:
    """Test that QUIT command causes clean exit."""
    print("\n=== Test: QUIT command ===")

    proc = start_renderer(socket_path)
    if not proc:
        return ShutdownResult("QUIT command", False, "Failed to start renderer")

    sock = connect_to_renderer(socket_path)
    if not sock:
        proc.kill()
        proc.wait()
        return ShutdownResult("QUIT command", False, "Failed to connect")

    cmd_id = [1]
    if not init_renderer(sock, cmd_id):
        sock.close()
        proc.kill()
        proc.wait()
        return ShutdownResult("QUIT command", False, "Failed to initialize")

    return _send_quit_and_wait(sock, proc, cmd_id)


def _send_quit_and_wait(sock, proc: subprocess.Popen, cmd_id: list[int]) -> ShutdownResult:
    """Send QUIT command and wait for clean exit."""
    try:
        resp = send_command(sock, {"command": "QUIT", "id": cmd_id[0]})
        _ = resp.get("success", False)
    except ConnectionError:
        pass  # Expected - connection closes on QUIT
    except Exception as e:
        sock.close()
        proc.kill()
        proc.wait()
        return ShutdownResult("QUIT command", False, f"Error sending QUIT: {e}")

    sock.close()
    return _wait_for_exit(proc)


def _wait_for_exit(proc: subprocess.Popen) -> ShutdownResult:
    """Wait for renderer process to exit and check result."""
    try:
        exit_code = proc.wait(timeout=5.0)
        stderr_output = proc.stderr.read() if proc.stderr else ""
        has_quit_event = '"event": "QUIT"' in stderr_output or '"event":"QUIT"' in stderr_output

        if exit_code == 0 and has_quit_event:
            return ShutdownResult("QUIT command", True, "Renderer exited cleanly with QUIT event")
        elif exit_code == 0:
            return ShutdownResult("QUIT command", True, "Renderer exited cleanly (no QUIT event seen)")
        else:
            return ShutdownResult("QUIT command", False, f"Exit code {exit_code}")
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        return ShutdownResult("QUIT command", False, "Renderer did not exit within timeout")


def test_quit_command(socket_path: str) -> None:
    """Pytest wrapper for QUIT command test."""
    cleanup_socket(socket_path)
    result = run_quit_command_test(socket_path)
    assert result.passed, result.details
