#!/usr/bin/env python3
"""Pure functions for processing paste content and inserting text at cursor.

This module provides functions for handling paste operations in the command
prompt, including whitespace stripping and cursor position management.
"""


def process_paste_text(text: str) -> str:
    """Strip leading and trailing whitespace from paste content.

    Args:
        text: The raw text from a paste operation.

    Returns:
        The text with leading and trailing whitespace removed.
        Internal whitespace (including newlines and tabs) is preserved.
    """
    return text.strip()


def insert_text_at_cursor(
    current_text: str, cursor_index: int, text_to_insert: str
) -> tuple[str, int]:
    """Insert text at the specified cursor position.

    Args:
        current_text: The current input text.
        cursor_index: Position where text should be inserted (0-based).
        text_to_insert: The text to insert.

    Returns:
        A tuple of (new_text, new_cursor_position) where new_cursor_position
        is cursor_index + len(text_to_insert).

    Raises:
        ValueError: If cursor_index is not in range [0, len(current_text)].
    """
    if cursor_index < 0 or cursor_index > len(current_text):
        raise ValueError(
            f"cursor_index {cursor_index} out of range "
            f"[0, {len(current_text)}]"
        )
    new_text = (
        current_text[:cursor_index]
        + text_to_insert
        + current_text[cursor_index:]
    )
    new_cursor = cursor_index + len(text_to_insert)
    return (new_text, new_cursor)


def handle_paste(
    current_text: str, cursor_index: int, paste_content: str
) -> tuple[str, int] | None:
    """Process and insert paste content at the cursor position.

    Strips leading and trailing whitespace from paste_content, then inserts
    the result at the cursor position. Returns None if the processed
    paste content is empty (indicating no-op).

    Args:
        current_text: The current input text.
        cursor_index: Position where text should be inserted (0-based).
        paste_content: The raw paste content.

    Returns:
        A tuple of (new_text, new_cursor_position) if paste content is
        non-empty after stripping, or None if the result would be empty.
    """
    processed = process_paste_text(paste_content)
    if not processed:
        return None
    return insert_text_at_cursor(current_text, cursor_index, processed)
