#!/usr/bin/env python3
"""Async netstring reader for stream communication.

Provides utilities for reading netstring-framed messages from async streams,
building on the core netstring encoding/decoding from the netstring module.
"""

import asyncio
import logging
from collections.abc import AsyncIterator

from platyplaty.netstring import (
    IncompleteNetstringError,
    MalformedNetstringError,
    decode_netstring,
)

logger = logging.getLogger(__name__)


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
