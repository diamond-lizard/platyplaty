"""Truncation utilities for entries with indicators (middle pane).

This module re-exports indicator truncation functions from their
respective modules for backward compatibility:
- truncate_file_with_indicator from truncation_file_indicator
- truncate_directory from truncation_directory
- truncate_symlink from truncation_symlink
"""

from platyplaty.ui.truncation_directory import truncate_directory
from platyplaty.ui.truncation_file_indicator import truncate_file_with_indicator
from platyplaty.ui.truncation_symlink import truncate_symlink

__all__ = [
    "truncate_file_with_indicator",
    "truncate_directory",
    "truncate_symlink",
]
