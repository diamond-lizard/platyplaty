"""Type definitions for the file browser widget.

This module provides dataclasses and type aliases used by the file
browser for representing right pane content.
"""

from dataclasses import dataclass
from pathlib import Path

from platyplaty.ui.directory_types import DirectoryListing


@dataclass
class RightPaneDirectory:
    """Right pane content showing a directory listing."""

    listing: DirectoryListing


@dataclass
class RightPaneFilePreview:
    """Right pane content showing lines from a file."""

    lines: tuple[str, ...]


@dataclass
class RightPaneEmpty:
    """Right pane content showing the 'empty' message."""

    pass


@dataclass
class RightPaneNoMilk:
    """Right pane content showing the 'no .milk files' message."""

    pass


@dataclass
class RightPaneBinaryFile:
    """Right pane content showing the 'BINARY FILE' message."""

    pass


class BinaryFileError(Exception):
    """Raised when a file cannot be decoded as UTF-8."""

    pass


RightPaneContent = (
    RightPaneDirectory
    | RightPaneFilePreview
    | RightPaneEmpty
    | RightPaneNoMilk
    | RightPaneBinaryFile
    | None
)


def read_file_preview_lines(path: Path) -> tuple[str, ...] | None:
    """Read lines from a file for preview.

    Args:
        path: Path to the file to read.

    Returns:
        Tuple of lines from the file, or None if file cannot be read.
    """
    try:
        with path.open('r', encoding='utf-8') as f:
            return tuple(f.readlines())
    except UnicodeDecodeError as e:
        raise BinaryFileError(str(path)) from e
    except OSError:
        return None


def render_file_preview_line(
    lines: tuple[str, ...], y: int, width: int
) -> str:
    """Render a single line of file preview.

    Args:
        lines: The file lines to display.
        y: The line number to render (0-indexed).
        width: The width of the pane.

    Returns:
        A string padded/truncated to the pane width.
    """
    if y >= len(lines):
        return " " * width
    line = lines[y].rstrip('\n\r')
    return line.ljust(width)[:width]
