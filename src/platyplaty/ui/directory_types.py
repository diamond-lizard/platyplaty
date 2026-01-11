"""Type definitions for directory listing.

This module provides the data types used to represent directory entries
and listing results in the file browser.
"""

from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path


class EntryType(Enum):
    """Type of directory entry."""

    DIRECTORY = auto()
    FILE = auto()
    SYMLINK_TO_DIRECTORY = auto()
    SYMLINK_TO_FILE = auto()
    BROKEN_SYMLINK = auto()


@dataclass(frozen=True)
class DirectoryEntry:
    """A single entry in a directory listing.

    Attributes:
        name: The entry name (filename or directory name).
        entry_type: The type of entry (directory, file, symlink, etc.).
        path: The absolute path to this entry.
    """

    name: str
    entry_type: EntryType
    path: Path


@dataclass(frozen=True)
class DirectoryListing:
    """Result of listing a directory.

    Attributes:
        entries: List of directory entries matching the filter.
        was_empty: True if directory had no entries at all.
        had_filtered_entries: True if some entries were filtered out.
        permission_denied: True if directory could not be read.
    """

    entries: list[DirectoryEntry]
    was_empty: bool
    had_filtered_entries: bool
    permission_denied: bool
