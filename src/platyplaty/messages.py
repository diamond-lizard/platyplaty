#!/usr/bin/env python3
"""Textual message types for worker-to-app communication."""

from textual.message import Message


class LogMessage(Message):
    """A log message to be displayed in the application's RichLog widget.

    Attributes:
        text: The message content to display.
        level: Optional severity level (debug, info, warning, error).
    """

    def __init__(self, text: str, level: str = "info") -> None:
        """Create a log message.

        Args:
            text: The message content to display.
            level: Severity level, one of: debug, info, warning, error.
        """
        self.text = text
        self.level = level
        super().__init__()
