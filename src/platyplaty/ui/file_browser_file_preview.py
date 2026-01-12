"""File preview creation for the file browser widget.

This module provides functions for creating file preview content,
including size checks, binary detection, and content reading.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from platyplaty.ui.file_browser_types import (
    RightPaneContent,
    RightPaneFilePreview,
    RightPaneBinaryFile,
    BinaryFileError,
)
from platyplaty.ui.file_browser_file_utils import read_file_preview_lines

if TYPE_CHECKING:
    from platyplaty.ui.directory_types import DirectoryEntry
    from platyplaty.ui.file_browser import FileBrowser


FILE_SIZE_LIMIT = 10 * 1024 * 1024  # 10 MB


def make_file_preview(
    browser: FileBrowser, entry: DirectoryEntry
) -> RightPaneContent:
    """Create file preview content for an entry.

    Args:
        browser: The file browser instance.
        entry: The directory entry to preview.

    Returns:
        RightPaneFilePreview with file lines, or None if unreadable.
    """
    file_path = browser.current_dir / entry.name
    # Check file size: empty or too large files trigger collapsed state
    try:
        file_size = file_path.stat().st_size
    except OSError:
        return None
    if file_size == 0 or file_size > FILE_SIZE_LIMIT:
        return None
    # Read file content, handling race conditions (file vanished after listing)
    pane_height = max(1, browser.size.height - 1)
    try:
        lines = read_file_preview_lines(file_path, pane_height)
    except (PermissionError, FileNotFoundError):
        return None
    except BinaryFileError:
        return RightPaneBinaryFile()
    if lines is None:
        return None
    return RightPaneFilePreview(lines)
