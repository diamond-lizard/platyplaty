#!/usr/bin/env python3
"""Playlist keybindings configuration for Platyplaty."""

from pydantic import BaseModel, ConfigDict, Field, model_validator

from platyplaty.types.keys import validate_key_list


class PlaylistKeybindings(BaseModel):
    """Keybindings for playlist section."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    _key_fields = (
        "play_previous", "play_next", "reorder_up", "reorder_down",
        "delete_from_playlist", "undo", "redo", "save_playlist",
        "shuffle_playlist", "toggle_autoplay", "page_up", "page_down",
        "navigate_to_first_preset", "navigate_to_last_preset",
    )
    play_previous: list[str] = Field(default=["shift+k"], alias="play-previous")
    play_next: list[str] = Field(default=["shift+j"], alias="play-next")
    reorder_up: list[str] = Field(default=["ctrl+k"], alias="reorder-up")
    reorder_down: list[str] = Field(default=["ctrl+j"], alias="reorder-down")
    delete_from_playlist: list[str] = Field(
        default=["shift+d", "delete"], alias="delete-from-playlist"
    )
    undo: list[str] = Field(default=["u"])
    redo: list[str] = Field(default=["ctrl+r"])
    save_playlist: list[str] = Field(default=["ctrl+s"], alias="save-playlist")
    shuffle_playlist: list[str] = Field(default=["s"], alias="shuffle-playlist")
    toggle_autoplay: list[str] = Field(default=["space"], alias="toggle-autoplay")
    page_up: list[str] = Field(default=["pageup"], alias="page-up")
    page_down: list[str] = Field(default=["pagedown"], alias="page-down")
    navigate_to_first_preset: list[str] = Field(
        default=["home"], alias="navigate-to-first-preset"
    )
    navigate_to_last_preset: list[str] = Field(
        default=["end"], alias="navigate-to-last-preset"
    )
    preset_duration: int = Field(
        default=30, ge=1, strict=True, alias="preset-duration"
    )

    @model_validator(mode="after")
    def validate_keys(self) -> "PlaylistKeybindings":
        """Validate all key names."""
        for name in self._key_fields:
            validate_key_list(getattr(self, name), f"playlist.{name}")
        return self
