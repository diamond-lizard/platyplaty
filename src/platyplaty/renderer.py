#!/usr/bin/env python3
"""Renderer subprocess management for Platyplaty.

This module handles starting the C++ renderer as a subprocess,
waiting for the SOCKET READY signal, and providing real-time
stderr passthrough.
"""

import asyncio
from typing import TextIO

from platyplaty.renderer_binary import find_renderer_binary


class RendererStartupError(Exception):
    """Raised when the renderer fails to start or become ready."""

async def start_renderer(socket_path: str) -> asyncio.subprocess.Process:
    """Start the renderer subprocess and wait for it to become ready.

    Args:
        socket_path: Path to the Unix domain socket for communication.

    Returns:
        The running subprocess.Process object.

    Raises:
        RendererNotFoundError: If the renderer binary is not found.
        RendererStartupError: If the renderer fails to start or become ready.
    """
    renderer_binary = find_renderer_binary()

    process = await asyncio.create_subprocess_exec(
        str(renderer_binary),
        "--socket-path", socket_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        start_new_session=True,
    )

    # Wait for SOCKET READY signal on stdout
    ready = await _wait_for_ready(process)
    if not ready:
        exit_code = process.returncode
        msg = f"Renderer exited before becoming ready (exit code {exit_code})"
        raise RendererStartupError(msg)

    return process


async def _wait_for_ready(process: asyncio.subprocess.Process) -> bool:
    """Wait for the renderer to print SOCKET READY on stdout.

    Args:
        process: The renderer subprocess.

    Returns:
        True if SOCKET READY was received, False if process exited first.
    """
    if process.stdout is None:
        return False

    while True:
        line = await process.stdout.readline()
        if not line:
            # Process exited or stdout closed
            return False
        if line == b"SOCKET READY\n":
            return True


async def stream_stderr(
    process: asyncio.subprocess.Process,
    output_stream: TextIO,
) -> None:
    """Stream renderer stderr to an output stream in real-time.

    Args:
        process: The renderer subprocess.
        output_stream: A file-like object with write() and flush() methods.
    """
    if process.stderr is None:
        return

    async for line in process.stderr:
        output_stream.write(line.decode())
        output_stream.flush()
