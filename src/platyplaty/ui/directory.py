"""Directory listing and filtering for the file browser.

This module provides functions to list directory contents with filtering
for .milk files, directories, and symlinks. It handles permission errors
gracefully and provides entry type information.
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
    """

    name: str
    entry_type: EntryType


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


def _get_entry_type(path: Path) -> EntryType:
    """Determine the type of a directory entry.

    Args:
        path: Path to the entry.

    Returns:
        The EntryType for this entry.
    """
    if path.is_symlink():
        try:
            target = path.resolve(strict=True)
            if target.is_dir():
                return EntryType.SYMLINK_TO_DIRECTORY
            return EntryType.SYMLINK_TO_FILE
        except OSError:
            return EntryType.BROKEN_SYMLINK
    elif path.is_dir():
        return EntryType.DIRECTORY
    return EntryType.FILE


def _should_include(path: Path, entry_type: EntryType) -> bool:
    """Check if an entry should be included in the listing.

    Filter rules:
    - Directories (excluding . and ..): include
    - .milk files (case-insensitive): include
    - Symlinks to directories or .milk files: include
    - Broken symlinks: only if name ends in .milk or has no extension

    Args:
        path: Path to the entry.
        entry_type: The type of the entry.

    Returns:
        True if entry should be included.
    """
    name = path.name

    # Exclude . and ..
    if name in (".", ".."):
        return False

    # Directories and symlinks to directories always included
    if entry_type in (EntryType.DIRECTORY, EntryType.SYMLINK_TO_DIRECTORY):
        return True

    # Check for .milk extension (case-insensitive)
    suffix = path.suffix.lower()
    is_milk = suffix == ".milk"

    # Files and symlinks to files: must be .milk
    if entry_type in (EntryType.FILE, EntryType.SYMLINK_TO_FILE):
        return is_milk

    # Broken symlinks: only if .milk extension or no extension
    if entry_type == EntryType.BROKEN_SYMLINK:
        has_no_extension = suffix == ""
        return is_milk or has_no_extension

    return False


def _sort_key(entry: DirectoryEntry) -> tuple[int, str]:
    """Generate sort key for directory entries.

    Sorting rules:
    - Directories and symlinks to directories come first
    - Then files, symlinks to files, and broken symlinks
    - Within each group, case-insensitive alphabetical order

    Args:
        entry: The directory entry to sort.

    Returns:
        Tuple of (priority, lowercase_name) for sorting.
    """
    # Priority: 0 = directories first, 1 = everything else
    is_dir_like = entry.entry_type in (
        EntryType.DIRECTORY,
        EntryType.SYMLINK_TO_DIRECTORY,
    )
    priority = 0 if is_dir_like else 1
    return (priority, entry.name.lower())


def list_directory(directory: Path) -> DirectoryListing:
    """List directory contents with filtering and sorting.

    Lists the contents of a directory, filtering for:
    - Directories (excluding . and ..)
    - .milk files (case-insensitive extension)
    - Symlinks to either of the above
    - Broken symlinks if name ends in .milk or has no extension

    Results are sorted case-insensitively with directories first.

    Args:
        directory: Path to the directory to list.

    Returns:
        DirectoryListing with entries and status flags.
    """
    try:
        all_entries = list(directory.iterdir())
    except PermissionError:
        return DirectoryListing(
            entries=[],
            was_empty=False,
            had_filtered_entries=False,
            permission_denied=True,
        )
    except OSError:
        return DirectoryListing(
            entries=[],
            was_empty=False,
            had_filtered_entries=False,
            permission_denied=True,
        )

    was_empty = len(all_entries) == 0

    # Build entries with type information and filter
    filtered_entries: list[DirectoryEntry] = []
    for path in all_entries:
        entry_type = _get_entry_type(path)
        if _should_include(path, entry_type):
            filtered_entries.append(DirectoryEntry(path.name, entry_type))

    had_filtered_entries = len(filtered_entries) < len(all_entries)

    # Sort entries
    sorted_entries = sorted(filtered_entries, key=_sort_key)

    return DirectoryListing(
        entries=sorted_entries,
        was_empty=was_empty,
        had_filtered_entries=had_filtered_entries,
        permission_denied=False,
    )
