#!/usr/bin/env python3
"""Configuration type definitions for Platyplaty."""

from pydantic import BaseModel, ConfigDict, Field, model_validator

from platyplaty.types.keys import (
    has_abbreviated_modifier,
    is_valid_key_name,
    warn_invalid_key,
)


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
            if has_abbreviated_modifier(key):
                msg = (
                    f"Abbreviated modifier in keybindings.renderer.{field_name}: "
                    f"'{key}'. "
                )
                msg += "Use full names: ctrl+, shift+, alt+"
                raise ValueError(msg)
            if not is_valid_key_name(key):
                warn_invalid_key(key, f"keybindings.renderer.{field_name}")
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
        if self.quit is not None and has_abbreviated_modifier(self.quit):
            msg = f"Abbreviated modifier in keybindings.client.quit: '{self.quit}'. "
            msg += "Use full names: ctrl+, shift+, alt+"
            raise ValueError(msg)
        if self.quit is not None and not is_valid_key_name(self.quit):
            warn_invalid_key(self.quit, "keybindings.client.quit")
        return self



def _validate_key_list(keys: list[str], field_path: str) -> None:
    """Validate a list of key names for file browser keybindings.

    Args:
        keys: List of key names to validate.
        field_path: Full path for error messages
            (e.g., keybindings.file_browser.nav_up).

    Raises:
        ValueError: If any key has an abbreviated modifier.
    """
    for key in keys:
        if has_abbreviated_modifier(key):
            msg = f"Abbreviated modifier in {field_path}: '{key}'. "
            msg += "Use full names: ctrl+, shift+, alt+"
            raise ValueError(msg)
        if not is_valid_key_name(key):
            warn_invalid_key(key, field_path)


class FileBrowserKeybindings(BaseModel):
    """Keybindings for file browser navigation.

    Uses array syntax to allow multiple keys per action. Empty array disables action.

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
    file_browser: FileBrowserKeybindings = Field(default_factory=FileBrowserKeybindings)

class Config(BaseModel):
    """Configuration for the Platyplaty visualizer.

    Attributes:
        preset_dirs: List of directories containing .milk preset files.
        audio_source: PulseAudio source name for audio capture.
        preset_duration: Seconds to display each preset before advancing.
        shuffle: Whether to randomize playlist order.
        loop: Whether to loop the playlist when reaching the end.
        fullscreen: Whether to start in fullscreen mode.
        keybindings: Keybindings for renderer and terminal.
    """

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    preset_dirs: list[str] = Field(alias="preset-dirs")
    audio_source: str = Field(default="@DEFAULT_SINK@.monitor", alias="audio-source")
    preset_duration: int = Field(default=30, ge=1, strict=True, alias="preset-duration")
    shuffle: bool = False
    loop: bool = True
    fullscreen: bool = False
    keybindings: Keybindings = Field(default_factory=Keybindings)
