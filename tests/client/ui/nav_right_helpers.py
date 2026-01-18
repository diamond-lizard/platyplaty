#!/usr/bin/env python3
"""Helper functions for right navigation tests.

This module provides utility functions and context managers for testing
move_right() behavior with inaccessible directories.
"""

from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from helpers import make_inaccessible


@contextmanager
def temporarily_inaccessible(path: Path) -> Generator[None, None, None]:
    """Context manager to temporarily make a path inaccessible.

    Makes the path inaccessible (chmod 000) on entry and restores
    original permissions on exit.

    Args:
        path: The path to make temporarily inaccessible.

    Yields:
        None
    """
    restore = make_inaccessible(path)
    try:
        yield
    finally:
        restore()
