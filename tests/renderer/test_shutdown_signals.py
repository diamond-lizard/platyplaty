#!/usr/bin/env python3
"""
Test signal-based shutdown paths (SIGINT and SIGTERM).

Tests that SIGINT and SIGTERM cause the renderer to exit cleanly.
"""

import signal
import subprocess

from process_helpers import cleanup_socket, connect_to_renderer, start_renderer
from shutdown_helpers import ShutdownResult, init_renderer


def _run_signal_test(socket_path: str, sig: signal.Signals, name: str) -> ShutdownResult:
    """Test that a signal causes clean exit."""
    print(f"\n=== Test: {name} ===")

    proc = start_renderer(socket_path)
    if not proc:
        return ShutdownResult(name, False, "Failed to start renderer")

    sock = connect_to_renderer(socket_path)
    if not sock:
        proc.kill()
        proc.wait()
        return ShutdownResult(name, False, "Failed to connect")

    cmd_id = [1]
    if not init_renderer(sock, cmd_id):
        sock.close()
        proc.kill()
        proc.wait()
        return ShutdownResult(name, False, "Failed to initialize")

    sock.close()
    proc.send_signal(sig)
    return _wait_for_signal_exit(proc, name)


def _wait_for_signal_exit(proc: subprocess.Popen, name: str) -> ShutdownResult:
    """Wait for renderer to exit after signal."""
    try:
        exit_code = proc.wait(timeout=5.0)
        if exit_code == 0:
            return ShutdownResult(name, True, "Renderer exited cleanly")
        else:
            return ShutdownResult(name, False, f"Exit code {exit_code}")
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        return ShutdownResult(name, False, "Renderer did not exit within timeout")


def run_sigint_test(socket_path: str) -> ShutdownResult:
    """Test that SIGINT causes clean exit."""
    return _run_signal_test(socket_path, signal.SIGINT, "SIGINT")


def run_sigterm_test(socket_path: str) -> ShutdownResult:
    """Test that SIGTERM causes clean exit."""
    return _run_signal_test(socket_path, signal.SIGTERM, "SIGTERM")


def test_sigint(socket_path: str) -> None:
    """Pytest wrapper for SIGINT test."""
    cleanup_socket(socket_path)
    result = run_sigint_test(socket_path)
    assert result.passed, result.details


def test_sigterm(socket_path: str) -> None:
    """Pytest wrapper for SIGTERM test."""
    cleanup_socket(socket_path)
    result = run_sigterm_test(socket_path)
    assert result.passed, result.details
