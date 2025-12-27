#!/usr/bin/env python3
"""Netstring encoding and decoding for socket communication.

Netstrings are a simple framing format: <length>:<payload>,
For example, "hello" becomes "5:hello,"

This module handles encoding Python strings to netstrings and decoding
netstrings back to strings, with support for buffered/partial reads.
"""

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
