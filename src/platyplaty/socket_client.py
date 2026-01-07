#!/usr/bin/env python3
"""Socket client for communicating with the platyplaty renderer.

This module provides an async socket client that sends commands to the
renderer using netstring-framed JSON and receives responses.
"""

import asyncio
import json
from asyncio import StreamReader, StreamWriter

from platyplaty.netstring import encode_netstring
from platyplaty.socket_response import recv_response, validate_response
from platyplaty.types import CommandResponse


class SocketClient:
    """Async socket client for renderer communication."""

    _reader: StreamReader | None
    _writer: StreamWriter | None
    _next_id: int
    _buffer: bytes
    _send_lock: asyncio.Lock

    def __init__(self) -> None:
        """Initialize the socket client."""
        self._reader = None
        self._writer = None
        self._next_id = 1
        self._buffer = b""
        self._send_lock = asyncio.Lock()

    async def connect(self, socket_path: str) -> None:
        """Connect to the renderer's Unix domain socket.

        Args:
            socket_path: Path to the Unix domain socket.
        """
        self._reader, self._writer = await asyncio.open_unix_connection(
            socket_path
        )

    def close(self) -> None:
        """Close the socket connection."""
        if self._writer is not None:
            self._writer.close()
            self._writer = None
        self._reader = None
        self._buffer = b""

    async def send_command(self, command: str, **params: object) -> CommandResponse:
        """Send a command to the renderer and wait for response.

        Args:
            command: The command name (e.g., "LOAD PRESET", "INIT").
            **params: Additional command parameters.

        Returns:
            CommandResponse with the renderer's response.

        Raises:
            ResponseIdMismatchError: If response ID doesn't match command ID.
            RendererError: If the renderer returns an error response.
        """
        if self._writer is None or self._reader is None:
            msg = "Not connected"
            raise RuntimeError(msg)

        async with self._send_lock:
            command_id = self._next_id
            self._next_id += 1

            message = {"command": command, "id": command_id, **params}
            data = encode_netstring(json.dumps(message))
            self._writer.write(data)
            await self._writer.drain()

            reader = self._reader
            response, self._buffer = await recv_response(reader, self._buffer)
            validate_response(response, command_id, command)

            return response
