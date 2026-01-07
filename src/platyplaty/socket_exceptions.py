#!/usr/bin/env python3
"""Exception classes for socket communication errors.

This module provides custom exception classes for handling errors
in communication with the renderer.
"""


class ResponseIdMismatchError(Exception):
    """Raised when response ID doesn't match command ID."""


class RendererError(Exception):
    """Raised when the renderer returns an error response."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
