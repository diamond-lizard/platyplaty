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
                msg += "Use full names: control-, shift-, alt-"
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
            msg += "Use full names: control-, shift-, alt-"
            raise ValueError(msg)
        if self.quit is not None and not is_valid_key_name(self.quit):
            warn_invalid_key(self.quit, "keybindings.client.quit")
        return self


class Keybindings(BaseModel):
    """Keybindings configuration container.

    Attributes:
        renderer: Keybindings for the renderer window.
        client: Keybindings for the terminal.
    """

    model_config = ConfigDict(extra="forbid")

    renderer: RendererKeybindings = Field(default_factory=RendererKeybindings)
    client: ClientKeybindings = Field(default_factory=ClientKeybindings)

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
