#!/usr/bin/env python3
"""Color constants for file browser UI.

This module defines color constants used throughout the file browser
for consistent styling of different item types.
"""

from platyplaty.ui.directory_types import EntryType

# Item type colors (foreground)
DIRECTORY_COLOR = "blue"
FILE_COLOR = "white"
SYMLINK_COLOR = "cyan"
BROKEN_SYMLINK_COLOR = "magenta"

# Background color
BACKGROUND_COLOR = "black"
DIMMED_COLOR = "bright_black"

# Empty/error message colors
EMPTY_MESSAGE_BG = "red"
EMPTY_MESSAGE_FG = "white"

# Bad preset colors (crashed the renderer)
BAD_PRESET_FG = "red"
BAD_PRESET_BG = "black"

# Selected item color (path display)
SELECTED_COLOR = "bright_white"


def get_entry_color(entry_type: EntryType) -> str:
    """Return the foreground color for a given entry type.

    Args:
        entry_type: The type of directory entry.

    Returns:
        A color name string suitable for Rich/Textual styling.
    """
    color_map = {
        EntryType.DIRECTORY: DIRECTORY_COLOR,
        EntryType.FILE: FILE_COLOR,
        EntryType.SYMLINK_TO_DIRECTORY: SYMLINK_COLOR,
        EntryType.SYMLINK_TO_FILE: SYMLINK_COLOR,
        EntryType.BROKEN_SYMLINK: BROKEN_SYMLINK_COLOR,
    }
    return color_map.get(entry_type, FILE_COLOR)


def get_inverted_colors(entry_type: EntryType) -> tuple[str, str]:
    """Return inverted colors (fg, bg) for a selected entry.

    For selection highlighting, colors are inverted: the normal foreground
    becomes the background, and black text appears on top.

    Args:
        entry_type: The type of directory entry.

    Returns:
        A tuple of (foreground, background) color names.
    """
    inverted_map = {
        EntryType.DIRECTORY: ("black", DIRECTORY_COLOR),
        EntryType.FILE: ("black", FILE_COLOR),
        EntryType.SYMLINK_TO_DIRECTORY: ("black", SYMLINK_COLOR),
        EntryType.SYMLINK_TO_FILE: ("black", SYMLINK_COLOR),
        EntryType.BROKEN_SYMLINK: ("black", BROKEN_SYMLINK_COLOR),
    }
    return inverted_map.get(entry_type, ("black", FILE_COLOR))
