#!/usr/bin/env python3
"""
Helper functions for shutdown path tests.

Provides shared utilities for testing renderer shutdown scenarios.
"""

import socket
from dataclasses import dataclass

from renderer_helpers import send_command

@dataclass
class ShutdownResult:
    """Result of a single shutdown test."""

    name: str
    passed: bool
    details: str


def init_renderer(sock: socket.socket, cmd_id: list[int]) -> bool:
    """Send CHANGE AUDIO SOURCE and INIT commands.

    Args:
        sock: Connected socket to renderer.
        cmd_id: Mutable list containing the next command ID.

    Returns:
        True if initialization succeeded, False otherwise.
    """
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

        resp = send_command(sock, {"command": "INIT", "id": cmd_id[0]})
        cmd_id[0] += 1
        if not resp.get("success"):
            print(f"  INIT failed: {resp.get('error')}")
            return False

        return True
    except Exception as e:
        print(f"  Init failed: {e}")
        return False
