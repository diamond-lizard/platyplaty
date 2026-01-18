#!/usr/bin/env python3
"""Error view keybindings configuration for Platyplaty."""

from pydantic import BaseModel, ConfigDict, Field, model_validator

from platyplaty.types.keys import validate_key_list


class ErrorViewKeybindings(BaseModel):
    """Keybindings for error view section."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    clear_errors: list[str] = Field(default=["c"], alias="clear-errors")

    @model_validator(mode="after")
    def validate_keys(self) -> "ErrorViewKeybindings":
        """Validate all key names."""
        for name in type(self).model_fields:
            validate_key_list(getattr(self, name), f"error-view.{name}")
        return self
