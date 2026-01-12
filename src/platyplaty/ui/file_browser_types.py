"""Type definitions for the file browser widget.

This module provides dataclasses and type aliases used by the file
browser for representing right pane content.
"""

from dataclasses import dataclass

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
