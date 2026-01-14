"""Unified truncation entry point for file browser entries.

This module provides a single function that handles truncation for all
entry types (directories, files, symlinks) and both display modes
(with or without indicators).
"""

from platyplaty.ui.directory_types import EntryType
from platyplaty.ui.truncation import split_filename, truncate_simple
from platyplaty.ui.truncation_directory import truncate_directory
from platyplaty.ui.truncation_file_indicator import truncate_file_with_indicator
from platyplaty.ui.truncation_filename import (
    truncate_filename_no_extension,
    truncate_filename_with_extension,
)
from platyplaty.ui.truncation_symlink import truncate_symlink


def _truncate_file_name_only(name: str, width: int) -> str:
    """Truncate a file name without indicator using extension rules.

    Args:
        name: The filename.
        width: Maximum width in characters.

    Returns:
        Truncated filename using multi-stage rules if it has an extension,
        or simple truncation if it doesn't.
    """
    base, ext = split_filename(name)
    if ext:
        return truncate_filename_with_extension(base, ext, width)
    return truncate_filename_no_extension(name, width)


def truncate_entry(
    name: str,
    entry_type: EntryType,
    indicator: str | int | None,
    width: int,
    show_indicator: bool,
) -> str:
    """Truncate an entry for display in file browser panes.

    Routes to appropriate truncation function based on entry type and
    whether indicators should be shown.

    Args:
        name: The entry name (filename or directory name).
        entry_type: The type of entry (DIRECTORY, FILE, SYMLINK_*, etc.).
        indicator: The indicator value. For directories, an int count.
            For files, a size string. For symlinks, the full indicator
            string (e.g., "-> 42" or "-> 1.5 K").
        width: Total available width in characters.
        show_indicator: True for middle pane (show indicators),
            False for left/right panes (name only).

    Returns:
        Truncated entry string, with or without indicator.
    """
    if entry_type == EntryType.DIRECTORY:
        if show_indicator and isinstance(indicator, int):
            return truncate_directory(name, indicator, width)
        return truncate_simple(name, width)

    if entry_type == EntryType.FILE:
        if show_indicator and isinstance(indicator, str):
            return truncate_file_with_indicator(name, indicator, width)
        return _truncate_file_name_only(name, width)

    if entry_type == EntryType.SYMLINK_TO_DIRECTORY:
        if show_indicator and isinstance(indicator, str):
            return truncate_symlink(name, indicator, width)
        return truncate_simple(name, width)

    if entry_type == EntryType.SYMLINK_TO_FILE:
        if show_indicator and isinstance(indicator, str):
            return truncate_symlink(name, indicator, width)
        return _truncate_file_name_only(name, width)

    if entry_type == EntryType.BROKEN_SYMLINK:
        if show_indicator and isinstance(indicator, str):
            return truncate_symlink(name, indicator, width)
        return _truncate_file_name_only(name, width)

    # Fallback for unknown types
    return truncate_simple(name, width)
