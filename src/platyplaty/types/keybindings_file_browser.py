#!/usr/bin/env python3
"""File browser keybindings configuration for Platyplaty."""

from pydantic import BaseModel, ConfigDict, Field, model_validator

from platyplaty.types.keys import validate_key_list


class FileBrowserKeybindings(BaseModel):
    """Keybindings for file browser section."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    open_parent: list[str] = Field(default=["h", "left"], alias="open-parent")
    add_preset_or_load_playlist: list[str] = Field(
        default=["a"], alias="add-preset-or-load-playlist"
    )
    play_previous_preset: list[str] = Field(
        default=["shift+k"], alias="play-previous-preset"
    )
    play_next_preset: list[str] = Field(
        default=["shift+j"], alias="play-next-preset"
    )

    @model_validator(mode="after")
    def validate_keys(self) -> "FileBrowserKeybindings":
        """Validate all key names."""
        for name in type(self).model_fields:
            validate_key_list(getattr(self, name), f"file-browser.{name}")
        return self
