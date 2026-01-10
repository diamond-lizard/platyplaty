#!/usr/bin/env python3
"""Tests for color constants and functions.

This module tests the color constants and get_entry_color function
used for styling different item types in the file browser.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.colors import (
    BACKGROUND_COLOR,
    BROKEN_SYMLINK_COLOR,
    DIRECTORY_COLOR,
    EMPTY_MESSAGE_BG,
    EMPTY_MESSAGE_FG,
    FILE_COLOR,
    SELECTED_COLOR,
    SYMLINK_COLOR,
)


class TestColorConstants:
    """Tests for color constant values."""

    def test_directory_color_is_blue(self) -> None:
        """Directory items should be blue."""
        assert DIRECTORY_COLOR == "blue"

    def test_file_color_is_white(self) -> None:
        """Regular file items should be white."""
        assert FILE_COLOR == "white"

    def test_symlink_color_is_cyan(self) -> None:
        """Valid symlink items should be cyan."""
        assert SYMLINK_COLOR == "cyan"

    def test_broken_symlink_color_is_magenta(self) -> None:
        """Broken symlink items should be magenta."""
        assert BROKEN_SYMLINK_COLOR == "magenta"

    def test_background_color_is_black(self) -> None:
        """Background should be black."""
        assert BACKGROUND_COLOR == "black"

    def test_empty_message_background_is_red(self) -> None:
        """Empty directory message background should be red."""
        assert EMPTY_MESSAGE_BG == "red"

    def test_empty_message_foreground_is_white(self) -> None:
        """Empty directory message foreground should be white."""
        assert EMPTY_MESSAGE_FG == "white"

    def test_selected_color_is_bright_white(self) -> None:
        """Selected item color should be bright white."""
        assert SELECTED_COLOR == "bright_white"
