#!/usr/bin/env python3
"""Helper functions for navigation memory tests.

This module provides utility functions for creating test directory
structures used in selection and scroll memory tests.
"""

from pathlib import Path


def create_dir_with_milk_files(
    parent: Path,
    filenames: list[str],
) -> None:
    """Create a directory with .milk files.

    Args:
        parent: The directory to create files in.
        filenames: List of filenames to create (without extension).
    """
    parent.mkdir(parents=True, exist_ok=True)
    for name in filenames:
        fname = f"{name}.milk" if not name.endswith(".milk") else name
        (parent / fname).write_text(name)


def create_numbered_milk_files(parent: Path, count: int) -> None:
    """Create a directory with numbered .milk files.

    Args:
        parent: The directory to create files in.
        count: Number of files to create (file_00.milk to file_{count-1}.milk).
    """
    parent.mkdir(parents=True, exist_ok=True)
    for i in range(count):
        name = f"file_{i:02d}.milk"
        (parent / name).write_text(f"content {i}")
