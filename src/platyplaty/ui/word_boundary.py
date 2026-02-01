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
