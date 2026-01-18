#!/usr/bin/env python3
"""
Test window close shutdown path.

Tests that closing the window causes the renderer to exit cleanly.
"""

import subprocess
import time

from ewmh_helpers import EWMH_AVAILABLE, close_window_by_name
from process_helpers import cleanup_socket, connect_to_renderer, start_renderer
from renderer_helpers import send_command
from shutdown_helpers import ShutdownResult, init_renderer


def run_window_close_test(socket_path: str) -> ShutdownResult:
    """Test that window close causes clean exit."""
    print("\n=== Test: Window close (uses EWMH) ===")

    proc = start_renderer(socket_path)
    if not proc:
        return ShutdownResult("Window close", False, "Failed to start renderer")

    sock = connect_to_renderer(socket_path)
    if not sock:
        proc.kill()
        proc.wait()
        return ShutdownResult("Window close", False, "Failed to connect")

    cmd_id = [1]
    if not init_renderer(sock, cmd_id):
        sock.close()
        proc.kill()
        proc.wait()
        return ShutdownResult("Window close", False, "Failed to initialize")

    return _show_and_close_window(sock, proc, cmd_id)


def _show_and_close_window(sock, proc, cmd_id: list[int]) -> ShutdownResult:
    """Show window and attempt to close it via EWMH."""
    try:
        resp = send_command(sock, {"command": "SHOW WINDOW", "id": cmd_id[0]})
        cmd_id[0] += 1
        if not resp.get("success"):
            sock.close()
            proc.kill()
            proc.wait()
            return ShutdownResult("Window close", False, f"SHOW WINDOW failed: {resp.get('error')}")
    except Exception as e:
        sock.close()
        proc.kill()
        proc.wait()
        return ShutdownResult("Window close", False, f"Error showing window: {e}")

    sock.close()
    return _close_via_ewmh(proc)


def _close_via_ewmh(proc: subprocess.Popen) -> ShutdownResult:
    """Close window using EWMH and wait for exit."""
    if not EWMH_AVAILABLE:
        proc.kill()
        proc.wait()
        return ShutdownResult("Window close", False, "ewmh not available (pip install ewmh)")

    time.sleep(0.5)

    if not close_window_by_name("Platyplaty"):
        proc.kill()
        proc.wait()
        return ShutdownResult("Window close", False, "Could not find window to close")

    print("  Sent close request via EWMH, waiting for renderer to exit...")
    return _wait_for_exit(proc)


def _wait_for_exit(proc: subprocess.Popen) -> ShutdownResult:
    """Wait for renderer to exit after window close."""
    try:
        exit_code = proc.wait(timeout=5.0)
        if exit_code == 0:
            return ShutdownResult("Window close", True, "Renderer exited cleanly after window close")
        else:
            return ShutdownResult("Window close", False, f"Exit code {exit_code}")
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        return ShutdownResult("Window close", False, "Renderer did not exit after window close")


def test_window_close(socket_path: str) -> None:
    """Pytest wrapper for window close test."""
    cleanup_socket(socket_path)
    result = run_window_close_test(socket_path)
    assert result.passed, result.details
