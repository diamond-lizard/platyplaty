#!/usr/bin/env python3
"""Word boundary detection for emacs-style editing.

This module provides functions for finding word boundaries using two definitions:
1. Alphanumeric words: sequences of alphanumeric characters (for Alt+B/F/D)
2. Unix words: sequences of non-whitespace characters (for Ctrl+W)
"""


def find_word_start_backward(text: str, cursor: int) -> int:
    """Find the start of the word at or before the cursor.

    Uses alphanumeric word definition: a word is a sequence of alphanumeric
    characters. Non-alphanumeric characters act as boundaries.

    Args:
        text: The input text to search.
        cursor: Current cursor position (0-indexed).

    Returns:
        Index of the start of the word. Returns 0 if no word exists before
        cursor or if cursor is at position 0.
    """
    if cursor == 0:
        return 0
    pos = cursor - 1
    while pos >= 0 and not text[pos].isalnum():
        pos -= 1
    if pos < 0:
        return 0
    while pos >= 0 and text[pos].isalnum():
        pos -= 1
    return pos + 1


def find_unix_word_start_backward(text: str, cursor: int) -> int:
    """Find the start of the unix word at or before the cursor.

    Uses unix word definition: a word is a sequence of non-whitespace
    characters. Only whitespace acts as a boundary, so slashes, hyphens,
    underscores, and dots are all part of the word.

    Args:
        text: The input text to search.
        cursor: Current cursor position (0-indexed).

    Returns:
        Index of the start of the word. Returns 0 if no word exists before
        cursor or if cursor is at position 0.
    """
    if cursor == 0:
        return 0
    pos = cursor - 1
    while pos >= 0 and text[pos].isspace():
        pos -= 1
    if pos < 0:
        return 0
    while pos >= 0 and not text[pos].isspace():
        pos -= 1
    return pos + 1


def find_word_end_forward(text: str, cursor: int) -> int:
    """Find the end of the word at or after the cursor.

    Uses alphanumeric word definition: a word is a sequence of alphanumeric
    characters. Non-alphanumeric characters act as boundaries.

    Args:
        text: The input text to search.
        cursor: Current cursor position (0-indexed).

    Returns:
        Index one past the end of the word. Returns len(text) if no word
        exists at or after cursor.
    """
    length = len(text)
    pos = cursor
    while pos < length and not text[pos].isalnum():
        pos += 1
    if pos >= length:
        return length
    while pos < length and text[pos].isalnum():
        pos += 1
    return pos


def find_path_word_start_backward(text: str, cursor: int) -> int:
    """Find the start of a path-aware word at or before the cursor.

    Uses path-aware word definition for Ctrl+W: slashes and whitespace act as
    boundaries, but "lone slashes" (preceded only by whitespace or start-of-line)
    are absorbed with the preceding word.

    Algorithm:
        1. Skip trailing whitespace backward (absorb into cut region)
        2. If at slashes, skip backward over all consecutive slashes
        3. Check what precedes the slashes:
            - If whitespace or start-of-line: "lone slash" - absorb and repeat from step 1
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
