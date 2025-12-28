#!/usr/bin/env python3
"""Socket client for communicating with the platyplaty renderer.

This module provides an async socket client that sends commands to the
renderer using netstring-framed JSON and receives responses.
"""

import asyncio
import json
from asyncio import StreamReader, StreamWriter

from platyplaty.netstring import (
    IncompleteNetstringError,
    decode_netstring,
    encode_netstring,
)
from platyplaty.types import CommandResponse


class ResponseIdMismatchError(Exception):
    """Raised when response ID doesn't match command ID."""


class RendererError(Exception):
    """Raised when the renderer returns an error response."""

    def __init__(self, message: str, command_id: int | None) -> None:
        super().__init__(message)
        self.command_id = command_id


class SocketClient:
    """Async socket client for renderer communication."""

    _reader: StreamReader | None
    _writer: StreamWriter | None
    _next_id: int
    _buffer: bytes

    def __init__(self) -> None:
        """Initialize the socket client."""
        self._reader = None
        self._writer = None
        self._next_id = 1
        self._buffer = b""

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

        command_id = self._next_id
        self._next_id += 1

        message = {"command": command, "id": command_id, **params}
        data = encode_netstring(json.dumps(message))
        self._writer.write(data)
        await self._writer.drain()

        response = await self._recv_response()
        if response.id != command_id:
            msg = f"Response ID {response.id} doesn't match command ID {command_id}"
            raise ResponseIdMismatchError(msg)

        if not response.success:
            raise RendererError(response.error or "Unknown error", response.id)

        return response

    def _try_decode_buffer(self) -> CommandResponse | None:
        """Try to decode a response from the buffer.

        Returns:
            CommandResponse if a complete message is in buffer, None otherwise.
        """
        try:
            payload, remaining = decode_netstring(self._buffer)
            self._buffer = remaining
            response_data = json.loads(payload)
            return CommandResponse.model_validate(response_data)
        except IncompleteNetstringError:
            return None

    async def _read_more_data(self) -> None:
        """Read more data from the socket into the buffer.

        Raises:
            ConnectionError: If the connection is closed.
        """
        if self._reader is None:
            msg = "Not connected"
            raise RuntimeError(msg)
        chunk = await self._reader.read(4096)
        if not chunk:
            msg = "Connection closed by renderer"
            raise ConnectionError(msg) from None
        self._buffer += chunk
    async def _recv_response(self) -> CommandResponse:
        """Receive and decode a response from the renderer.

        Uses buffering to handle partial reads.

        Returns:
            CommandResponse parsed from the netstring-framed JSON.

        Raises:
            ConnectionError: If the connection is closed unexpectedly.
        """
        if self._reader is None:
            msg = "Not connected"
            raise RuntimeError(msg)

        result = self._try_decode_buffer()
        while result is None:
            await self._read_more_data()
            result = self._try_decode_buffer()
        return result
