"""Indicator cache refresh functions.

This module provides functions to invalidate and refresh cached
indicator values when navigation changes selection.
"""

from pathlib import Path

from platyplaty.ui.directory_types import EntryType
from platyplaty.ui.indicators import (
    count_directory_contents,
    directory_count_cache,
)
from platyplaty.ui.size_format import (
    file_size_cache,
    get_file_size,
    get_symlink_size,
    symlink_size_cache,
)


def refresh_indicator_cache(entry_type: EntryType, path: Path) -> None:
    """Invalidate cache for an entry and recalculate its indicator.

    Called when selection changes to refresh indicator values for
    entries that remain visible. The cache key is deleted first,
    then the appropriate function is called to recalculate.

    Args:
        entry_type: Type of the entry.
        path: Path to the entry.
    """
    key = (path,)
    if entry_type == EntryType.DIRECTORY:
        directory_count_cache.pop(key, None)
        count_directory_contents(path)
    elif entry_type == EntryType.FILE:
        file_size_cache.pop(key, None)
        get_file_size(path)
    elif entry_type == EntryType.SYMLINK_TO_DIRECTORY:
        directory_count_cache.pop(key, None)
        count_directory_contents(path)
    elif entry_type == EntryType.SYMLINK_TO_FILE:
        file_size_cache.pop(key, None)
        get_file_size(path)
    elif entry_type == EntryType.BROKEN_SYMLINK:
        symlink_size_cache.pop(key, None)
        get_symlink_size(path)
