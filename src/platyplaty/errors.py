#!/usr/bin/env python3
"""Exception classes for Platyplaty."""


class StartupError(Exception):
    """Raised when startup fails."""

class InaccessibleDirectoryError(Exception):
    """Raised when a directory cannot be accessed.

    Attributes:
        path: The path to the inaccessible directory.
    """

    def __init__(self, path: str) -> None:
        """Initialize with the inaccessible path.

        Args:
            path: The path to the inaccessible directory.
        """
        self.path = path
        super().__init__(f"Cannot access directory: {path}")
