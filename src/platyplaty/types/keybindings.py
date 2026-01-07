#!/usr/bin/env python3
"""Keybinding container and file browser keybinding definitions."""

from pydantic import BaseModel, ConfigDict, Field, model_validator

from platyplaty.types.renderer_keybindings import (
    ClientKeybindings,
    RendererKeybindings,
    _validate_single_key,
)


def _validate_key_list(keys: list[str], field_path: str) -> None:
    """Validate a list of key names for file browser keybindings.

    Args:
        keys: List of key names to validate.
        field_path: Full path for error messages.

    Raises:
        ValueError: If any key has an abbreviated modifier.
    """
    for key in keys:
        _validate_single_key(key, field_path)


class FileBrowserKeybindings(BaseModel):
    """Keybindings for file browser navigation.

    Uses array syntax to allow multiple keys per action. Empty array disables.

    Attributes:
        nav_up: Keys to move selection up.
        nav_down: Keys to move selection down.
        nav_left: Keys to navigate to parent directory.
        nav_right: Keys to navigate into directory or open file.
    """

    model_config = ConfigDict(extra="forbid")

    nav_up: list[str] = Field(default=["k", "up"])
    nav_down: list[str] = Field(default=["j", "down"])
    nav_left: list[str] = Field(default=["h", "left"])
    nav_right: list[str] = Field(default=["l", "right"])

    @model_validator(mode="after")
    def validate_keys(self) -> "FileBrowserKeybindings":
        """Validate key names and warn for unrecognized keys."""
        for field_name in ("nav_up", "nav_down", "nav_left", "nav_right"):
            keys = getattr(self, field_name)
            field_path = f"keybindings.file_browser.{field_name}"
            _validate_key_list(keys, field_path)
        return self


class Keybindings(BaseModel):
    """Keybindings configuration container.

    Attributes:
        renderer: Keybindings for the renderer window.
        client: Keybindings for the terminal.
        file_browser: Keybindings for file browser navigation.
    """

    model_config = ConfigDict(extra="forbid")

    renderer: RendererKeybindings = Field(default_factory=RendererKeybindings)
    client: ClientKeybindings = Field(default_factory=ClientKeybindings)
    file_browser: FileBrowserKeybindings = Field(
        default_factory=FileBrowserKeybindings
    )
