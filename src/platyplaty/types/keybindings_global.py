#!/usr/bin/env python3
"""Global keybindings configuration for Platyplaty."""

from pydantic import BaseModel, ConfigDict, Field, model_validator

from platyplaty.types.keys import validate_key_list


class GlobalKeybindings(BaseModel):
    """Keybindings available in all sections."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    switch_focus: list[str] = Field(default=["tab"], alias="switch-focus")
    quit: list[str] = Field(default=["q"])
    navigate_up: list[str] = Field(default=["k", "up"], alias="navigate-up")
    navigate_down: list[str] = Field(
        default=["j", "down"], alias="navigate-down"
    )
    open_selected: list[str] = Field(
        default=["l", "right"], alias="open-selected"
    )
    view_errors: list[str] = Field(default=["e"], alias="view-errors")
    play_selection: list[str] = Field(default=["enter"], alias="play-selection")

    @model_validator(mode="after")
    def validate_keys(self) -> "GlobalKeybindings":
        """Validate all key names."""
        for name in self.model_fields:
            validate_key_list(getattr(self, name), f"global.{name}")
        return self
