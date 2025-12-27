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

import json
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from typing import Optional

try:
    from ewmh import EWMH
    EWMH_AVAILABLE = True
except ImportError:
    EWMH_AVAILABLE = False


@dataclass
class _ShutdownResult:
    """Result of a single test."""
    name: str
    passed: bool
    details: str


def close_window_by_name(window_name: str) -> bool:
    """Close a window by name using EWMH protocol.
    
    Args:
        window_name: The window title to search for.
    
    Returns:
        True if window was found and close request sent, False otherwise.
    """
    if not EWMH_AVAILABLE:
        return False
    
    ewmh = EWMH()
    for win in ewmh.getClientList():
        if win is None:
            continue
        try:
            wm_name = win.get_wm_name()
            if wm_name and window_name in wm_name:
                ewmh.setCloseWindow(win)
                ewmh.display.flush()
                return True
        except Exception:
            continue
    return False

def encode_netstring(payload: str) -> bytes:
    """Encode a string as a netstring."""
    encoded = payload.encode('utf-8')
    return f"{len(encoded)}:{payload},".encode('utf-8')


def decode_netstring(data: bytes) -> tuple[Optional[str], int]:
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
        if ready:
            line = proc.stdout.readline() if proc.stdout else ""
            if line.strip() == "SOCKET READY":
                return True
    return False


def init_renderer(sock: socket.socket, cmd_id: list[int]) -> bool:
    """Send CHANGE AUDIO SOURCE and INIT commands."""
    try:
        resp = send_command(sock, {
            "command": "CHANGE AUDIO SOURCE",
            "id": cmd_id[0],
            "audio_source": "@DEFAULT_SINK@.monitor"
        })
        cmd_id[0] += 1
        if not resp.get("success"):
            print(f"  CHANGE AUDIO SOURCE failed: {resp.get('error')}")
            return False

        resp = send_command(sock, {
            "command": "INIT",
            "id": cmd_id[0]
        })
        cmd_id[0] += 1
        if not resp.get("success"):
            print(f"  INIT failed: {resp.get('error')}")
            return False

        return True
    except Exception as e:
        print(f"  Init failed: {e}")
        return False


def start_renderer(socket_path: str) -> Optional[subprocess.Popen]:
    """Start the renderer process."""
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


def connect_to_renderer(socket_path: str) -> Optional[socket.socket]:
    """Connect to the renderer's Unix socket."""
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


def _run_quit_command(socket_path: str) -> _ShutdownResult:
    """Test 1: QUIT command causes clean exit."""
    print("\n=== Test 1: QUIT command ===")

    proc = start_renderer(socket_path)
    if not proc:
        return _ShutdownResult("QUIT command", False, "Failed to start renderer")

    sock = connect_to_renderer(socket_path)
    if not sock:
        proc.kill()
        proc.wait()
        return _ShutdownResult("QUIT command", False, "Failed to connect")

    cmd_id = [1]
    if not init_renderer(sock, cmd_id):
        sock.close()
        proc.kill()
        proc.wait()
        return _ShutdownResult("QUIT command", False, "Failed to initialize")

    # Send QUIT - connection may close before we read response, which is okay
    try:
        resp = send_command(sock, {"command": "QUIT", "id": cmd_id[0]})
        _ = resp.get("success", False)  # Response received but we check exit code
    except ConnectionError:
        # Connection closed - this is expected for QUIT, check process exit below
        pass
    except Exception as e:
        sock.close()
        proc.kill()
        proc.wait()
        return _ShutdownResult("QUIT command", False, f"Error sending QUIT: {e}")
    
    sock.close()

    # Wait for process to exit
    try:
        exit_code = proc.wait(timeout=5.0)
        stderr_output = proc.stderr.read() if proc.stderr else ""

        # Check for QUIT event in stderr
        has_quit_event = '"event": "QUIT"' in stderr_output or '"event":"QUIT"' in stderr_output

        if exit_code == 0 and has_quit_event:
            return _ShutdownResult("QUIT command", True, "Renderer exited cleanly with QUIT event")
        elif exit_code == 0:
            return _ShutdownResult("QUIT command", True, "Renderer exited cleanly (no QUIT event seen)")
        else:
            return _ShutdownResult("QUIT command", False, f"Exit code {exit_code}")
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        return _ShutdownResult("QUIT command", False, "Renderer did not exit within timeout")


def _run_sigint(socket_path: str) -> _ShutdownResult:
    """Test 3: SIGINT causes clean exit."""
    print("\n=== Test 3: SIGINT ===")

    proc = start_renderer(socket_path)
    if not proc:
        return _ShutdownResult("SIGINT", False, "Failed to start renderer")

    sock = connect_to_renderer(socket_path)
    if not sock:
        proc.kill()
        proc.wait()
        return _ShutdownResult("SIGINT", False, "Failed to connect")

    cmd_id = [1]
    if not init_renderer(sock, cmd_id):
        sock.close()
        proc.kill()
        proc.wait()
        return _ShutdownResult("SIGINT", False, "Failed to initialize")

    sock.close()

    # Send SIGINT
    proc.send_signal(signal.SIGINT)

    try:
        exit_code = proc.wait(timeout=5.0)
        if exit_code == 0:
            return _ShutdownResult("SIGINT", True, "Renderer exited cleanly")
        else:
            return _ShutdownResult("SIGINT", False, f"Exit code {exit_code}")
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        return _ShutdownResult("SIGINT", False, "Renderer did not exit within timeout")


def _run_sigterm(socket_path: str) -> _ShutdownResult:
    """Test 4: SIGTERM causes clean exit."""
    print("\n=== Test 4: SIGTERM ===")

    proc = start_renderer(socket_path)
    if not proc:
        return _ShutdownResult("SIGTERM", False, "Failed to start renderer")

    sock = connect_to_renderer(socket_path)
    if not sock:
        proc.kill()
        proc.wait()
        return _ShutdownResult("SIGTERM", False, "Failed to connect")

    cmd_id = [1]
    if not init_renderer(sock, cmd_id):
        sock.close()
        proc.kill()
        proc.wait()
        return _ShutdownResult("SIGTERM", False, "Failed to initialize")

    sock.close()

    # Send SIGTERM
    proc.send_signal(signal.SIGTERM)

    try:
        exit_code = proc.wait(timeout=5.0)
        if exit_code == 0:
            return _ShutdownResult("SIGTERM", True, "Renderer exited cleanly")
        else:
            return _ShutdownResult("SIGTERM", False, f"Exit code {exit_code}")
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        return _ShutdownResult("SIGTERM", False, "Renderer did not exit within timeout")


def _run_client_disconnect(socket_path: str) -> _ShutdownResult:
    """Test 5: Client disconnect - renderer stays alive."""
    print("\n=== Test 5: Client disconnect (renderer should stay alive) ===")

    proc = start_renderer(socket_path)
    if not proc:
        return _ShutdownResult("Client disconnect", False, "Failed to start renderer")

    sock = connect_to_renderer(socket_path)
    if not sock:
        proc.kill()
        proc.wait()
        return _ShutdownResult("Client disconnect", False, "Failed to connect")

    cmd_id = [1]
    if not init_renderer(sock, cmd_id):
        sock.close()
        proc.kill()
        proc.wait()
        return _ShutdownResult("Client disconnect", False, "Failed to initialize")

    # Close socket without QUIT
    print("  Disconnecting client...")
    sock.close()

    # Wait a moment
    time.sleep(1.0)

    # Check if renderer is still running
    if proc.poll() is not None:
        exit_code = proc.returncode
        return _ShutdownResult("Client disconnect", False,
                         f"Renderer exited unexpectedly with code {exit_code}")

    # Try to reconnect
    print("  Attempting to reconnect...")
    sock2 = connect_to_renderer(socket_path)
    if not sock2:
        proc.kill()
        proc.wait()
        return _ShutdownResult("Client disconnect", False, "Could not reconnect")

    # New client should be able to send commands (already initialized)
    # QUIT may close connection before we read response - that's okay
    try:
        _ = send_command(sock2, {"command": "QUIT", "id": 1})
        sock2.close()
    except ConnectionError:
        # Connection closed - expected for QUIT
        sock2.close()
    except Exception as e:
        sock2.close()
        proc.kill()
        proc.wait()
        return _ShutdownResult("Client disconnect", False, f"Error with new client: {e}")
    
    # Check that renderer exits cleanly
    try:
        exit_code = proc.wait(timeout=5.0)
        if exit_code == 0:
            return _ShutdownResult("Client disconnect", True,
                             "Renderer stayed alive and accepted new client")
        else:
            return _ShutdownResult("Client disconnect", False, f"Exit code {exit_code}")
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        return _ShutdownResult("Client disconnect", False, "Renderer did not exit after QUIT")


def _run_window_close(socket_path: str) -> _ShutdownResult:
    """Test 2: Window close causes clean exit (uses EWMH to close window)."""
    print("\n=== Test 2: Window close (uses EWMH) ===")

    proc = start_renderer(socket_path)
    if not proc:
        return _ShutdownResult("Window close", False, "Failed to start renderer")

    sock = connect_to_renderer(socket_path)
    if not sock:
        proc.kill()
        proc.wait()
        return _ShutdownResult("Window close", False, "Failed to connect")

    cmd_id = [1]
    if not init_renderer(sock, cmd_id):
        sock.close()
        proc.kill()
        proc.wait()
        return _ShutdownResult("Window close", False, "Failed to initialize")

    # Show the window
    try:
        resp = send_command(sock, {"command": "SHOW WINDOW", "id": cmd_id[0]})
        cmd_id[0] += 1
        if not resp.get("success"):
            sock.close()
            proc.kill()
            proc.wait()
            return _ShutdownResult("Window close", False, f"SHOW WINDOW failed: {resp.get('error')}")
    except Exception as e:
        sock.close()
        proc.kill()
        proc.wait()
        return _ShutdownResult("Window close", False, f"Error showing window: {e}")

    sock.close()

    # Check if ewmh is available
    if not EWMH_AVAILABLE:
        proc.kill()
        proc.wait()
        return _ShutdownResult("Window close", False, "ewmh not available (pip install ewmh)")

    # Give window time to appear
    time.sleep(0.5)

    # Close window using ewmh
    if not close_window_by_name("Platyplaty"):
        proc.kill()
        proc.wait()
        return _ShutdownResult("Window close", False, "Could not find window to close")

    print("  Sent close request via EWMH, waiting for renderer to exit...")

    try:
        exit_code = proc.wait(timeout=5.0)
        if exit_code == 0:
            return _ShutdownResult("Window close", True, "Renderer exited cleanly after window close")
        else:
            return _ShutdownResult("Window close", False, f"Exit code {exit_code}")
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        return _ShutdownResult("Window close", False, "Renderer did not exit after window close")



# Pytest wrapper functions
def test_quit_command(socket_path: str) -> None:
    """Pytest wrapper for QUIT command test."""
    result = _run_quit_command(socket_path)
    assert result.passed, result.details


def test_sigint(socket_path: str) -> None:
    """Pytest wrapper for SIGINT test."""
    result = _run_sigint(socket_path)
    assert result.passed, result.details


def test_sigterm(socket_path: str) -> None:
    """Pytest wrapper for SIGTERM test."""
    result = _run_sigterm(socket_path)
    assert result.passed, result.details


def test_client_disconnect(socket_path: str) -> None:
    """Pytest wrapper for client disconnect test."""
    result = _run_client_disconnect(socket_path)
    assert result.passed, result.details


def test_window_close(socket_path: str) -> None:
    """Pytest wrapper for window close test."""
    result = _run_window_close(socket_path)
    assert result.passed, result.details

def main() -> int:
    """Run all shutdown tests."""
    print("=" * 60)
    print("Platyplaty Renderer Shutdown Path Tests")
    print("=" * 60)

    # Check renderer exists
    if not os.path.exists("build/platyplaty-renderer"):
        print("\nERROR: build/platyplaty-renderer not found.")
        print("Please run 'make' first.")
        return 1

    # Create temp socket path
    socket_path = os.path.join(tempfile.gettempdir(), f"platyplaty-test-{os.getpid()}.sock")

    # Clean up any stale socket
    if os.path.exists(socket_path):
        os.unlink(socket_path)

    results: list[_ShutdownResult] = []

    try:
        # Run automated tests first
        cleanup_socket(socket_path)
        results.append(_run_quit_command(socket_path))
        cleanup_socket(socket_path)
        results.append(_run_sigint(socket_path))
        cleanup_socket(socket_path)
        results.append(_run_sigterm(socket_path))
        cleanup_socket(socket_path)
        results.append(_run_client_disconnect(socket_path))

        # Run window close test (automated with EWMH)
        cleanup_socket(socket_path)
        results.append(_run_window_close(socket_path))

    finally:
        # Clean up socket file
        if os.path.exists(socket_path):
            os.unlink(socket_path)

    # Print summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = 0
    failed = 0
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"  [{status}] {r.name}: {r.details}")
        if r.passed:
            passed += 1
        else:
            failed += 1

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
