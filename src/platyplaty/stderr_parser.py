#!/usr/bin/env python3
"""Parse PLATYPLATY stderr events from the renderer.

The renderer emits netstring-framed JSON events on stderr for asynchronous
notifications. This module detects and parses these events, passing through
non-PLATYPLATY output unchanged.

Event format: <length>:{"source": "PLATYPLATY", ...},
Event types: DISCONNECT, AUDIO_ERROR, QUIT
"""

import json
import re
import sys

from platyplaty.netstring import (
    MalformedNetstringError,
    decode_netstring,
)
from platyplaty.types import StderrEvent

# Pattern to detect potential netstring start: digits followed by colon
_NETSTRING_START = re.compile(r"^\d+:")


def is_potential_netstring(line: str) -> bool:
    """Check if a line looks like it might start a netstring.

    Args:
        line: A line of stderr output.

    Returns:
        True if the line starts with digits followed by a colon.
    """
    return bool(_NETSTRING_START.match(line))


def parse_stderr_event(line: str) -> StderrEvent | None:
    """Attempt to parse a PLATYPLATY event from a stderr line.

    Args:
        line: A line of stderr output.

    Returns:
        StderrEvent if the line is a valid PLATYPLATY event, None otherwise.
        Returns None for malformed netstrings (pass through as regular output).
    """
    if not is_potential_netstring(line):
        return None

    try:
        payload, _ = decode_netstring(line.encode("utf-8"))
        data = json.loads(payload)
    except (MalformedNetstringError, json.JSONDecodeError):
        return None

    if not isinstance(data, dict) or data.get("source") != "PLATYPLATY":
        return None

    try:
        return StderrEvent.model_validate(data)
    except Exception:  # noqa: BLE001
        return None


def log_audio_error(event: StderrEvent) -> None:
    """Log an AUDIO_ERROR event to stderr.

    Args:
        event: The AUDIO_ERROR event to log.
    """
    msg = f"Audio error: {event.reason}, visualization continues silently"
    print(msg, file=sys.stderr)
