"""Directory accessibility check for navigation.

This module provides a helper function to check if a directory
is accessible. This is a package-private function used by
the nav_state module family.
"""

from pathlib import Path

from platyplaty.errors import InaccessibleDirectoryError


def check_directory_accessible(path: Path) -> None:
    """Check if a directory is accessible.

    Args:
        path: The path to check.

    Raises:
        InaccessibleDirectoryError: If directory cannot be accessed.
    """
    try:
        list(path.iterdir())
    except PermissionError:
        raise InaccessibleDirectoryError(str(path)) from None
    except OSError:
        raise InaccessibleDirectoryError(str(path)) from None
