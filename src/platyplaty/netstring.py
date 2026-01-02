#!/usr/bin/env python3
"""Netstring encoding and decoding for socket communication.

Netstrings are a simple framing format: <length>:<payload>,
For example, "hello" becomes "5:hello,"

This module handles encoding Python strings to netstrings and decoding
netstrings back to strings, with support for buffered/partial reads.
"""

import asyncio
import logging
from collections.abc import AsyncIterator

logger = logging.getLogger(__name__)

MAX_PAYLOAD_SIZE = 65536  # 64KB maximum payload size


class NetstringError(Exception):
    """Base exception for netstring encoding/decoding errors."""


class PayloadTooLargeError(NetstringError):
    """Raised when payload exceeds maximum size."""


class MalformedNetstringError(NetstringError):
    """Raised when netstring format is invalid."""


class IncompleteNetstringError(NetstringError):
    """Raised when more data is needed to complete the netstring."""


def encode_netstring(payload: str) -> bytes:
    """Encode a string as a netstring.

    Args:
        payload: The string to encode.

    Returns:
        Netstring-encoded bytes in format <length>:<payload>,

    Raises:
        PayloadTooLargeError: If payload exceeds MAX_PAYLOAD_SIZE bytes.
    """
    data = payload.encode('utf-8')
    if len(data) > MAX_PAYLOAD_SIZE:
        msg = f"Payload size {len(data)} exceeds maximum {MAX_PAYLOAD_SIZE}"
        raise PayloadTooLargeError(msg)
    return f"{len(data)}:".encode('ascii') + data + b","


def decode_netstring(data: bytes) -> tuple[str, bytes]:
    """Decode a netstring from bytes.

    This function is liberal in what it accepts: leading zeros in the
    length prefix are tolerated (though we never produce them).

    Args:
        data: Bytes that may contain a complete netstring.

    Returns:
        Tuple of (decoded payload string, remaining bytes after netstring).

    Raises:
        IncompleteNetstringError: If data doesn't contain a complete netstring.
        MalformedNetstringError: If the netstring format is invalid.
        PayloadTooLargeError: If the declared length exceeds MAX_PAYLOAD_SIZE.
    """
    colon_pos = data.find(b':')
    if colon_pos == -1:
        if len(data) > 6:
            raise MalformedNetstringError("No colon found in length prefix")
        raise IncompleteNetstringError("Waiting for colon in length prefix")
    length_bytes = data[:colon_pos]
    if not length_bytes:
        raise MalformedNetstringError("Empty length prefix")
    try:
        length = int(length_bytes.decode('ascii'))
    except (ValueError, UnicodeDecodeError) as e:
        raise MalformedNetstringError(f"Invalid length prefix: {e}") from e
    if length < 0:
        raise MalformedNetstringError("Negative length not allowed")
    if length > MAX_PAYLOAD_SIZE:
        msg = f"Declared length {length} exceeds maximum {MAX_PAYLOAD_SIZE}"
        raise PayloadTooLargeError(msg)
    end_pos = colon_pos + 1 + length
    if len(data) < end_pos + 1:
        raise IncompleteNetstringError("Waiting for complete payload")
    if data[end_pos] != ord(b','):
        raise MalformedNetstringError("Missing trailing comma")
    payload_bytes = data[colon_pos + 1:end_pos]
    try:
        payload = payload_bytes.decode('utf-8')
    except UnicodeDecodeError as e:
        raise MalformedNetstringError(f"Invalid UTF-8 in payload: {e}") from e
    return payload, data[end_pos + 1:]


def _extract_netstrings(buffer: bytes) -> tuple[list[str], bytes, bool]:
    """Extract complete netstrings from buffer.

    Returns:
        Tuple of (payloads, remaining_buffer, should_abort).
        should_abort is True if a malformed netstring was encountered.
    """
    payloads: list[str] = []
    while buffer:
        try:
            payload, buffer = decode_netstring(buffer)
            payloads.append(payload)
        except IncompleteNetstringError:
            break
        except MalformedNetstringError as e:
            logger.error("Malformed netstring: %s", e)
            return payloads, buffer, True
    return payloads, buffer, False


async def read_netstrings_from_stderr(
    stderr: asyncio.StreamReader,
) -> AsyncIterator[str]:
    """Read netstring-framed messages from stderr stream.

    Yields:
        Decoded netstring payloads as they become available.
    """
    buffer = b""
    while True:
        chunk = await stderr.read(4096)
        if not chunk:
            break
        buffer += chunk
        payloads, buffer, abort = _extract_netstrings(buffer)
        for payload in payloads:
            yield payload
        if abort:
            return
    if buffer:
        logger.warning("Incomplete netstring at EOF: %r", buffer)
