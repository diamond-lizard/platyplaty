#!/usr/bin/env python3
"""Response handling utilities for socket communication.

This module provides helper functions for parsing and validating
responses from the renderer.
"""

import json
from asyncio import StreamReader

from platyplaty.netstring import IncompleteNetstringError, decode_netstring
from platyplaty.socket_exceptions import RendererError, ResponseIdMismatchError
from platyplaty.types import CommandResponse


def try_decode_from_buffer(
    buffer: bytes,
) -> tuple[CommandResponse | None, bytes]:
    """Try to decode a response from a buffer.

    Args:
        buffer: The byte buffer containing potential netstring data.

    Returns:
        Tuple of (CommandResponse or None, remaining buffer bytes).
        If no complete message is available, returns (None, original buffer).
    """
    try:
        payload, remaining = decode_netstring(buffer)
        response_data = json.loads(payload)
        return CommandResponse.model_validate(response_data), remaining
    except IncompleteNetstringError:
        return None, buffer


def validate_response(
    response: CommandResponse,
    command_id: int,
    command: str,
) -> None:
    """Validate a response and raise appropriate errors if invalid.

    Args:
        response: The response from the renderer.
        command_id: The expected command ID.
        command: The command name (for error messages).

    Raises:
        ResponseIdMismatchError: If response ID doesn't match command ID.
        RendererError: If the renderer returns an error response.
    """
    if response.id != command_id:
        error_text = response.error or ""
        msg = (
            f"Response ID {response.id} doesn't match "
            f"command ID {command_id}, error message: '{error_text}'"
        )
        raise ResponseIdMismatchError(msg)

    if not response.success:
        error_text = response.error or ""
        msg = (
            f"Command '{command}' (ID {command_id}) failed, "
            f"error message: '{error_text}'"
        )
        raise RendererError(msg)


async def recv_response(
    reader: StreamReader,
    buffer: bytes,
) -> tuple[CommandResponse, bytes]:
    """Receive and decode a response from the renderer.

    Uses buffering to handle partial reads.

    Args:
        reader: The async stream reader.
        buffer: The current buffer contents.

    Returns:
        Tuple of (CommandResponse, remaining buffer bytes).

    Raises:
        ConnectionError: If the connection is closed unexpectedly.
    """
    result, buffer = try_decode_from_buffer(buffer)
    while result is None:
        chunk = await reader.read(4096)
        if not chunk:
            msg = "Connection closed by renderer"
            raise ConnectionError(msg) from None
        buffer = buffer + chunk
        result, buffer = try_decode_from_buffer(buffer)
    return result, buffer
