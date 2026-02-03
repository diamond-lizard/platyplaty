#!/usr/bin/env python3
"""Forward cut boundary detection for Alt+D."""


def find_path_cut_end_forward(text: str, cursor: int) -> int:
    """Find the end of a path-aware word for Alt+D cutting.

    Cuts forward to the end of the current path component but STOPS BEFORE
    any trailing slash. When starting on whitespace or a slash, absorbs
    the slash and cuts through the following component.

    Key difference from Alt+F movement:
        - Alt+F includes trailing slashes when moving
        - Alt+D stops before trailing slashes when cutting
        - When starting on a word, Alt+D does NOT absorb a lone slash after it

    Algorithm:
        1. If cursor is at end, return cursor (no-op)
        2. Skip forward over any leading whitespace
        3. After skipping whitespace, check current position:
            a. If at a slash (lone slash), absorb it and cut through following component
            b. If at a non-slash character, cut through the component
        4. Cut forward through the path component but STOP BEFORE any trailing slash

    Args:
        text: The input text to search.
        cursor: Current cursor position (0-indexed).

    Returns:
        Index of the cut end (position after the last character to cut).

    Examples:
        >>> find_path_cut_end_forward("load /foo/bar", 0)  # from start
        4  # cuts "load" only, does NOT absorb lone slash
        >>> find_path_cut_end_forward(" /foo/bar", 0)  # space then slash
        5  # cuts " /foo" (skip space, absorb slash, cut through foo)
        >>> find_path_cut_end_forward("/foo/bar", 0)  # leading slash
        4  # cuts "/foo" (absorb leading slash, cut through foo)
    """
    length = len(text)
    if cursor >= length:
        return cursor
    pos = cursor
    started_on_whitespace_or_slash = text[pos].isspace() or text[pos] == '/'
    if text[pos].isspace():
        pos = _skip_whitespace_forward(text, pos, length)
        if pos >= length:
            return length
    if text[pos] == '/':
        pos = _skip_slashes_forward(text, pos, length)
        if pos >= length:
            return length
        return _cut_through_component(text, pos, length)
    if started_on_whitespace_or_slash:
        return _cut_through_component(text, pos, length)
    return _cut_through_component(text, pos, length)


def _cut_through_component(text: str, pos: int, length: int) -> int:
    """Cut through a component, stopping before trailing slashes."""
    while pos < length and text[pos] != '/' and not text[pos].isspace():
        pos += 1
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
