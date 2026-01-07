#!/usr/bin/env python3
"""Renderer and client keybinding type definitions for Platyplaty."""

from pydantic import BaseModel, ConfigDict, model_validator

from platyplaty.types.keys import (
    has_abbreviated_modifier,
    is_valid_key_name,
    warn_invalid_key,
)


def _validate_single_key(key: str, field_path: str) -> None:
    """Validate a single key name and raise/warn as appropriate.

    Args:
        key: The key name to validate.
        field_path: Full path for error messages.

    Raises:
        ValueError: If the key has an abbreviated modifier.
    """
    if has_abbreviated_modifier(key):
        msg = f"Abbreviated modifier in {field_path}: '{key}'. "
        msg += "Use full names: ctrl+, shift+, alt+"
        raise ValueError(msg)
    if not is_valid_key_name(key):
        warn_invalid_key(key, field_path)


class RendererKeybindings(BaseModel):
    """Keybindings for the renderer window.

    Attributes:
        next_preset: Key to advance to the next preset.
        previous_preset: Key to go back to the previous preset.
        quit: Key to quit the application.
    """

    model_config = ConfigDict(extra="forbid")

    next_preset: str = "n"
    previous_preset: str = "p"
    quit: str = "q"

    @model_validator(mode="after")
    def validate_keys(self) -> "RendererKeybindings":
        """Validate key names and warn for unrecognized keys."""
        for field_name in ("next_preset", "previous_preset", "quit"):
            key = getattr(self, field_name)
            field_path = f"keybindings.renderer.{field_name}"
            _validate_single_key(key, field_path)
        return self


class ClientKeybindings(BaseModel):
    """Keybindings for the terminal.

    Attributes:
        quit: Key to quit the application (optional).
    """

    model_config = ConfigDict(extra="forbid")

    quit: str | None = None

    @model_validator(mode="after")
    def validate_keys(self) -> "ClientKeybindings":
        """Validate key names and warn for unrecognized keys."""
        if self.quit is not None:
            _validate_single_key(self.quit, "keybindings.client.quit")
        return self
