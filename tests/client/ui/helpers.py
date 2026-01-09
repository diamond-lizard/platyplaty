#!/usr/bin/env python3
"""Helper functions for filesystem setup in navigation tests.

This module provides utility functions for creating test directory
structures, symlinks, and managing file permissions.
"""

import os
from pathlib import Path
from typing import Callable


def make_inaccessible(path: Path) -> Callable[[], None]:
    """Make a directory inaccessible and return a cleanup function.

    Sets chmod 000 on the directory to simulate permission denied.
    Returns a cleanup function that restores permissions.

    Args:
        path: The directory path to make inaccessible.

    Returns:
        A cleanup function that restores original permissions.
    """
    original_mode = path.stat().st_mode
    os.chmod(path, 0o000)

    def restore() -> None:
        os.chmod(path, original_mode)

    return restore


def make_broken_symlink(link_path: Path, target_name: str = "nonexistent") -> None:
    """Create a symlink pointing to a nonexistent target.

    Args:
        link_path: Where to create the symlink.
        target_name: Name of the nonexistent target.
    """
    link_path.symlink_to(target_name)


def make_symlink_to_dir(link_path: Path, target_dir: Path) -> None:
    """Create a symlink pointing to a directory.

    Args:
        link_path: Where to create the symlink.
        target_dir: The directory to link to.
    """
    link_path.symlink_to(target_dir)


def make_symlink_to_file(link_path: Path, target_file: Path) -> None:
    """Create a symlink pointing to a file.

    Args:
        link_path: Where to create the symlink.
        target_file: The file to link to.
    """
    link_path.symlink_to(target_file)
