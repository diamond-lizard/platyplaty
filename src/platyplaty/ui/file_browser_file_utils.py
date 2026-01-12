"""File utility functions for the file browser widget.

This module provides functions for reading and rendering file preview
content. These are package-private functions.
"""

from pathlib import Path

from platyplaty.ui.file_browser_types import BinaryFileError


def read_file_preview_lines(path: Path, max_lines: int | None = None) -> tuple[str, ...] | None:
    """Read lines from a file for preview.

    Args:
        path: Path to the file to read.
        max_lines: Maximum number of lines to read, or None for all.

    Returns:
        Tuple of lines (stripped of trailing newlines), or None if file cannot be read.
    """
    try:
        with path.open('r', encoding='utf-8') as f:
            if max_lines is None:
                return tuple(line.rstrip('\n\r') for line in f.readlines())
            return tuple(line.rstrip('\n\r') for _, line in zip(range(max_lines), f))
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
    line = lines[y]
    return line.ljust(width)[:width]
