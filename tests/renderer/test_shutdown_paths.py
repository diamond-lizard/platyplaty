#!/usr/bin/env python3
"""
Test script for Platyplaty renderer shutdown paths.

Tests the following shutdown scenarios:
1. QUIT command - renderer should exit cleanly
2. Window close - renderer should exit cleanly (uses ewmh to simulate X button click)
3. SIGINT - renderer should exit cleanly
4. SIGTERM - renderer should exit cleanly
5. Client disconnect - renderer should stay alive and accept new client

Usage: ./tests/renderer/test_shutdown_paths.py
"""

import os
import sys
import tempfile

from process_helpers import cleanup_socket
from shutdown_helpers import ShutdownResult
from test_shutdown_disconnect import run_client_disconnect_test
from test_shutdown_quit import run_quit_command_test
from test_shutdown_signals import run_sigint_test, run_sigterm_test
from test_shutdown_window import run_window_close_test


def main() -> int:
    """Run all shutdown tests."""
    print("=" * 60)
    print("Platyplaty Renderer Shutdown Path Tests")
    print("=" * 60)

    if not os.path.exists("build/platyplaty-renderer"):
        print("\nERROR: build/platyplaty-renderer not found.")
        print("Please run 'make' first.")
        return 1

    socket_path = os.path.join(tempfile.gettempdir(), f"platyplaty-test-{os.getpid()}.sock")
    cleanup_socket(socket_path)

    results = _run_all_tests(socket_path)
    cleanup_socket(socket_path)

    return _print_summary(results)


def _run_all_tests(socket_path: str) -> list[ShutdownResult]:
    """Run all shutdown tests and return results."""
    results: list[ShutdownResult] = []

    cleanup_socket(socket_path)
    results.append(run_quit_command_test(socket_path))

    cleanup_socket(socket_path)
    results.append(run_sigint_test(socket_path))

    cleanup_socket(socket_path)
    results.append(run_sigterm_test(socket_path))

    cleanup_socket(socket_path)
    results.append(run_client_disconnect_test(socket_path))

    cleanup_socket(socket_path)
    results.append(run_window_close_test(socket_path))

    return results


def _print_summary(results: list[ShutdownResult]) -> int:
    """Print test summary and return exit code."""
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed

    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"  [{status}] {r.name}: {r.details}")

    print("-" * 60)
    print(f"Total: {passed} passed, {failed} failed")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nTest interrupted.")
        sys.exit(1)
