#!/usr/bin/env python3
"""Event type definitions for Platyplaty."""

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Discriminator, Tag



class KeyPressedEvent(BaseModel):
    """A KEY_PRESSED event with key information."""

    model_config = ConfigDict(extra="forbid")

    source: Literal["PLATYPLATY"]
    event: Literal["KEY_PRESSED"]
    key: str


class ReasonEvent(BaseModel):
    """A DISCONNECT, AUDIO_ERROR, or QUIT event with reason."""

    model_config = ConfigDict(extra="forbid")

    source: Literal["PLATYPLATY"]
    event: Literal["DISCONNECT", "AUDIO_ERROR", "QUIT"]
    reason: str


def _get_event_discriminator(v: dict[str, Any] | BaseModel) -> str:
    """Get discriminator value for StderrEvent union.

    Args:
        v: Raw dict or already-validated model.

    Returns:
        The event type string for discrimination.
    """
    if isinstance(v, dict):
        return str(v.get("event", ""))
    event = getattr(v, "event", None)
    return str(event) if event is not None else ""


# Discriminated union: pydantic selects model based on event field
# Discriminated union: pydantic selects model based on event field
# Tag values must match what _get_event_discriminator returns
StderrEvent = Annotated[
    Annotated[KeyPressedEvent, Tag("KEY_PRESSED")]
    | Annotated[ReasonEvent, Tag("DISCONNECT")]
    | Annotated[ReasonEvent, Tag("AUDIO_ERROR")]
    | Annotated[ReasonEvent, Tag("QUIT")],
    Discriminator(_get_event_discriminator),
]
