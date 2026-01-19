"""Directory listing for the file browser.

This module provides the main function to list directory contents with
filtering for .milk and .platy files, directories, and symlinks.
"""

from pathlib import Path

from platyplaty.ui.directory_entry import get_entry_type, should_include
from platyplaty.ui.directory_types import (
    DirectoryEntry,
    DirectoryListing,
    EntryType,
)


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
    - .milk and .platy files (case-insensitive extension)
    - Symlinks to directories, .milk files, or .platy files
    - Broken symlinks if name ends in .milk, .platy, or has no extension

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
        entry_type = get_entry_type(path)
        if should_include(path, entry_type):
            filtered_entries.append(DirectoryEntry(path.name, entry_type, path))

    had_filtered_entries = len(filtered_entries) < len(all_entries)

    # Sort entries
    sorted_entries = sorted(filtered_entries, key=_sort_key)

    return DirectoryListing(
        entries=sorted_entries,
        was_empty=was_empty,
        had_filtered_entries=had_filtered_entries,
        permission_denied=False,
    )
