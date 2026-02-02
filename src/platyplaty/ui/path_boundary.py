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
