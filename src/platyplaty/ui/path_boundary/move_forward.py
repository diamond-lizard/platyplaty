#!/usr/bin/env python3
"""Forward movement boundary detection for Alt+F."""


def find_path_word_end_forward(text: str, cursor: int) -> int:
    """Find the end of a path-aware word for Alt+F movement.

    Moves forward to the end of the current path component including its
    trailing slash. When starting on whitespace or a leading slash at
    position 0, handles lone slashes as their own unit.

    Algorithm:
        1. If cursor is at end, return len(text)
        2. If starting on whitespace, skip forward over it:
            - If now at a slash, this is a "lone slash" unit - return position after it
            - Otherwise, proceed to move through the component
        3. If starting on a slash at position 0, return 1 (leading slash is own unit)
        4. If starting on a non-whitespace non-slash character:
            - Move forward through the word
            - Include any trailing slashes as part of the component
            - When hitting whitespace, check for a lone slash after it:
                if found, absorb the whitespace and the slash, then stop

    Args:
        text: The input text to search.
        cursor: Current cursor position (0-indexed).

    Returns:
        Index of the end of the path word (position after the last character).

    Examples:
        >>> find_path_word_end_forward("load /foo/bar", 0)  # from start
        6  # moves past "load /" (absorbs lone slash after whitespace)
        >>> find_path_word_end_forward("load /foo/bar", 6)  # at 'f' in foo
        10  # moves past "foo/"
        >>> find_path_word_end_forward("/foo/bar", 0)  # leading slash
        1  # leading slash is own unit
        >>> find_path_word_end_forward(" /foo/bar", 0)  # space then slash
        2  # skip space, lone slash is own unit
    """
    length = len(text)
    if cursor >= length:
        return length
    pos = cursor
    # Check if starting on whitespace
    if text[pos].isspace():
        pos = _skip_whitespace_forward(text, pos, length)
        if pos >= length:
            return length
        # After whitespace, if at a slash, it's a lone slash unit
        if text[pos] == '/':
            return _skip_slashes_forward(text, pos, length)
    # Check if starting on a slash at position 0 (leading slash)
    if text[pos] == '/' and cursor == 0:
        return _skip_slashes_forward(text, pos, length)
    # If starting on a slash (not at position 0), include it with the component
    if text[pos] == '/':
        pos = _skip_slashes_forward(text, pos, length)
        if pos >= length:
            return length
    # Move through the word (non-whitespace, non-slash characters)
    while pos < length and text[pos] != '/' and not text[pos].isspace():
        pos += 1
    # Include trailing slashes as part of the component
    if pos < length and text[pos] == '/':
        pos = _skip_slashes_forward(text, pos, length)
    # Check for lone slash after whitespace (absorb it)
    if pos < length and text[pos].isspace():
        ws_start = pos
        pos = _skip_whitespace_forward(text, pos, length)
        if pos < length and text[pos] == '/':
            return _skip_slashes_forward(text, pos, length)
        return ws_start
    return pos


def _skip_whitespace_forward(text: str, pos: int, length: int) -> int:
    """Skip forward over whitespace characters."""
    while pos < length and text[pos].isspace():
        pos += 1
    return pos


def _skip_slashes_forward(text: str, pos: int, length: int) -> int:
    """Skip forward over consecutive slashes."""
    pos += 1
    while pos < length and text[pos] == '/':
        pos += 1
    return pos
