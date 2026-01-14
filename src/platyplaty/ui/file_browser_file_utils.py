"""File utility functions for the file browser widget.

This module provides functions for reading and rendering file preview
content. These are package-private functions.
"""

from pathlib import Path

from platyplaty.ui.file_browser_types import BinaryFileError


def truncate_line(line: str, width: int) -> str:
    """Truncate a line to fit within a given display width.

    Expands tabs to 4 spaces and handles wide Unicode characters.
    If the line fits within width, returns it as-is (with tabs expanded).
    If it exceeds width, truncates at the display width boundary.

    Args:
        line: The line to truncate.
        width: The maximum display width.

    Returns:
        The line truncated to fit within width.
    """
    from rich.cells import cell_len

    # Expand tabs to 4 spaces
    expanded = line.expandtabs(4)

    # If it fits, return as-is
    if cell_len(expanded) <= width:
        return expanded

    # Truncate character by character until we fit
    result = []
    current_width = 0
    for char in expanded:
        char_width = cell_len(char)
        if current_width + char_width > width:
            break
        result.append(char)
        current_width += char_width
    return ''.join(result)

def _read_lines_from_file(f, max_lines: int | None) -> tuple[str, ...]:
    """Read lines from an open file handle.

    Args:
        f: Open file handle to read from.
        max_lines: Maximum number of lines to read, or None for all.

    Returns:
        Tuple of lines stripped of trailing newlines.
    """
    if max_lines is None:
        return tuple(line.rstrip('\n\r') for line in f.readlines())
    return tuple(
        line.rstrip('\n\r')
        for _, line in zip(range(max_lines), f, strict=False)
    )

def read_file_preview_lines(
    path: Path, max_lines: int | None = None,
) -> tuple[str, ...] | None:
    """Read lines from a file for preview.

    Args:
        path: Path to the file to read.
        max_lines: Maximum number of lines to read, or None for all.

    Returns:
        Tuple of lines (stripped of trailing newlines), or None if file cannot be read.
    """
    try:
        with path.open('r', encoding='utf-8') as f:
            return _read_lines_from_file(f, max_lines)
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
    truncated = truncate_line(line, width)
    return truncated.ljust(width)
