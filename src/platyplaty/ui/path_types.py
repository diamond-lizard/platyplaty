#!/usr/bin/env python3
"""Path component type definitions for path display.

This module provides the data types used to represent path components
with type information for coloring in the path display line.
"""

from dataclasses import dataclass
from enum import Enum, auto


class PathComponentType(Enum):
    """Type of path component for coloring purposes."""

    DIRECTORY = auto()
    SYMLINK = auto()
    BROKEN_SYMLINK = auto()
    FILE = auto()


@dataclass(frozen=True)
class PathComponent:
    """A single component of a path for display purposes.

    Attributes:
        name: The component name (directory or file name).
        component_type: The type of component for coloring.
        is_selected: True if this is the selected (final) component.
    """

    name: str
    component_type: PathComponentType
    is_selected: bool = False
