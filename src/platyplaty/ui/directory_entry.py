"""Directory entry type detection and filtering.

This module provides helper functions for determining entry types,
filtering entries, and sorting directory listings.
"""

from pathlib import Path

from platyplaty.ui.directory_types import EntryType


def _get_symlink_type(path: Path) -> EntryType:
    """Determine the type of a symlink entry.

    Args:
        path: Path to the symlink.

    Returns:
        The EntryType for this symlink (to directory, to file, or broken).
    """
    try:
        target = path.resolve(strict=True)
        if target.is_dir():
            return EntryType.SYMLINK_TO_DIRECTORY
        return EntryType.SYMLINK_TO_FILE
    except OSError:
        return EntryType.BROKEN_SYMLINK


def get_entry_type(path: Path) -> EntryType:
    """Determine the type of a directory entry.

    Args:
        path: Path to the entry.

    Returns:
        The EntryType for this entry.
    """
    if path.is_symlink():
        return _get_symlink_type(path)
    if path.is_dir():
        return EntryType.DIRECTORY
    return EntryType.FILE


def should_include(path: Path, entry_type: EntryType) -> bool:
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
