#!/usr/bin/env python3
"""Parse PLATYPLATY stderr events from the renderer.

The renderer emits JSON events on stderr for asynchronous notifications.
Netstring framing is handled by netstring.read_netstrings_from_stderr();
this module validates and parses the decoded JSON payloads.

Event types: DISCONNECT, AUDIO_ERROR, QUIT, KEY_PRESSED
"""

import json
import sys

from pydantic import TypeAdapter

from platyplaty.types import ReasonEvent, StderrEvent

# TypeAdapter for validating the StderrEvent discriminated union
_STDERR_EVENT_ADAPTER: TypeAdapter[StderrEvent] = TypeAdapter(StderrEvent)


def parse_stderr_event(line: str) -> StderrEvent | None:
    """Attempt to parse a PLATYPLATY event from a stderr line.

    Args:
        line: A line of stderr output.

    Returns:
        StderrEvent if the line is a valid PLATYPLATY event, None otherwise.
        Returns None for malformed netstrings (pass through as regular output).
    """
    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, dict) or data.get("source") != "PLATYPLATY":
        return None

    try:
        return _STDERR_EVENT_ADAPTER.validate_python(data)
    except Exception:  # noqa: BLE001
        return None


def log_audio_error(event: ReasonEvent) -> None:
    """Log an AUDIO_ERROR event to stderr.

    Args:
        event: The AUDIO_ERROR event to log.
    """
    msg = f"Audio error: {event.reason}, visualization continues silently"
    print(msg, file=sys.stderr)
