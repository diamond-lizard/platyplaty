"""Filename truncation for the status line.

Handles truncating playlist filenames using file browser rules.
"""

from platyplaty.ui.truncation_filename import (
    truncate_filename_no_extension,
    truncate_filename_with_extension,
)


DIRTY_PREFIX = "* "


def format_filename(basename: str, dirty: bool, available: int) -> str:
    """Format the filename with dirty prefix and truncation.

    Args:
        basename: The filename (basename only).
        dirty: Whether to add the "* " prefix.
        available: Available width for the entire file part.

    Returns:
        Formatted filename, possibly truncated.
    """
    prefix = DIRTY_PREFIX if dirty else ""
    name_width = available - len(prefix)
    if name_width <= 0:
        return prefix[:available] if available > 0 else ""
    truncated_name = truncate_basename(basename, name_width)
    return prefix + truncated_name


def truncate_basename(basename: str, width: int) -> str:
    """Truncate basename following file browser rules.

    Args:
        basename: The filename to truncate.
        width: Maximum width.

    Returns:
        Truncated filename.
    """
    if len(basename) <= width:
        return basename
    dot_index = basename.rfind(".")
    if dot_index > 0:
        name = basename[:dot_index]
        ext = basename[dot_index:]
        return truncate_filename_with_extension(name, ext, width)
    return truncate_filename_no_extension(basename, width)
