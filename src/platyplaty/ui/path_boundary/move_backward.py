#!/usr/bin/env python3
"""Backward movement boundary detection for Alt+B."""


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
