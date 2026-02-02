#!/usr/bin/env python3
"""Path-aware word boundary detection for emacs-style editing.

This module provides functions for finding word boundaries that treat slashes
as boundaries, optimized for editing filesystem paths in the command prompt.
"""


def find_path_word_start_backward(text: str, cursor: int) -> int:
    """Find the start of a path-aware word at or before the cursor.

    Uses path-aware word definition for Ctrl+W: slashes and whitespace act as
    boundaries, but "lone slashes" (preceded only by whitespace or start-of-line)
    are absorbed with the preceding word.

    Algorithm:
        1. Skip trailing whitespace backward (absorb into cut region)
        2. If at slashes, skip backward over all consecutive slashes
        3. Check what precedes the slashes:
            - If whitespace or start-of-line: "lone slash" - absorb and
              repeat from step 1
            - If non-whitespace: cut backward through component to next slash/whitespace
        4. If at non-slash after step 1, cut back through component

    Args:
        text: The input text to search.
        cursor: Current cursor position (0-indexed).

    Returns:
        Index of the start of the path word. Returns 0 if cursor is at 0.

    Examples:
        >>> find_path_word_start_backward("/foo/bar/baz", 12)  # from end
        9  # cuts "baz"
        >>> find_path_word_start_backward("/foo/bar/baz ", 13)  # trailing space
        9  # cuts "baz " (space absorbed)
        >>> find_path_word_start_backward("load /", 6)  # lone slash
        0  # cuts "load /" entirely
    """
    if cursor == 0:
        return 0
    pos = cursor - 1
    while pos >= 0 and text[pos].isspace():
        pos -= 1
    if pos < 0:
        return 0
    while pos >= 0 and text[pos] == '/':
        pos -= 1
    if pos < 0:
        return 0
    if text[pos].isspace():
        return find_path_word_start_backward(text, pos + 1)
    while pos >= 0 and text[pos] != '/' and not text[pos].isspace():
        pos -= 1
    return pos + 1


def find_path_component_start_backward(text: str, cursor: int) -> int:
    """Find the start of the previous path component for Alt+B movement.

    Moves backward to the start of the previous path component, skipping over
    slashes. Unlike find_path_word_start_backward, this function lands AT the
    start of a component (the first character), not at a slash.

    Algorithm:
        1. If cursor is 0, return 0
        2. Starting from cursor-1, scan backward:
            - First skip over any trailing slashes
        3. If now at a component character (non-slash, non-whitespace):
            - Skip backward through the component until reaching a slash,
              whitespace, or start-of-string
        4. If whitespace is encountered, skip over it and any following slashes,
            then continue scanning for the previous component
        5. The leading slash at position 0 is a navigable position

    Args:
        text: The input text to search.
        cursor: Current cursor position (0-indexed).

    Returns:
        Index of the start of the previous path component.

    Examples:
        >>> find_path_component_start_backward("/foo/bar/baz", 12)  # from end
        9  # lands at 'b' in baz
        >>> find_path_component_start_backward("/foo/bar/baz", 9)
        5  # lands at 'b' in bar
        >>> find_path_component_start_backward("/foo/bar/baz", 5)
        1  # lands at 'f' in foo
        >>> find_path_component_start_backward("/foo/bar/baz", 1)
        0  # lands at leading slash
        >>> find_path_component_start_backward("load /foo", 6)  # at 'f'
        0  # skips slash, space, lands at 'l' in load
    """
    if cursor == 0:
        return 0
    pos = cursor - 1
    # Skip trailing slashes
    while pos >= 0 and text[pos] == '/':
        pos -= 1
    if pos < 0:
        return 0
    # If at whitespace, skip over it and any following slashes
    if text[pos].isspace():
        while pos >= 0 and text[pos].isspace():
            pos -= 1
        if pos < 0:
            return 0
        while pos >= 0 and text[pos] == '/':
            pos -= 1
        if pos < 0:
            return 0
    # Now at a component character, scan backward to find start
    while pos >= 0 and text[pos] != '/' and not text[pos].isspace():
        pos -= 1
    return pos + 1


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
        while pos < length and text[pos].isspace():
            pos += 1
        if pos >= length:
            return length
        # After whitespace, if at a slash, it's a lone slash unit
        if text[pos] == '/':
            pos += 1
            # Absorb consecutive slashes
            while pos < length and text[pos] == '/':
                pos += 1
            return pos
    # Check if starting on a slash at position 0 (leading slash)
    if text[pos] == '/' and cursor == 0:
        pos += 1
        # Absorb consecutive leading slashes
        while pos < length and text[pos] == '/':
            pos += 1
        return pos
    # If starting on a slash (not at position 0), include it with the component
    if text[pos] == '/':
        while pos < length and text[pos] == '/':
            pos += 1
        if pos >= length:
            return length
    # Move through the word (non-whitespace, non-slash characters)
    while pos < length and text[pos] != '/' and not text[pos].isspace():
        pos += 1
    # Include trailing slashes as part of the component
    while pos < length and text[pos] == '/':
        pos += 1
    # Check for lone slash after whitespace (absorb it)
    if pos < length and text[pos].isspace():
        ws_start = pos
        while pos < length and text[pos].isspace():
            pos += 1
        if pos < length and text[pos] == '/':
            # Absorb the lone slash
            pos += 1
            while pos < length and text[pos] == '/':
                pos += 1
            return pos
        # No lone slash after whitespace, return before the whitespace
        return ws_start
    return pos
