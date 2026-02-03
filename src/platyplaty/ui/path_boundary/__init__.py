#!/usr/bin/env python3
"""Path-aware word boundary detection for emacs-style editing.

This package provides functions for finding word boundaries that treat slashes
as boundaries, optimized for editing filesystem paths in the command prompt.

Functions:
    find_path_word_start_backward: Backward cut boundary for Ctrl+W
    find_path_component_start_backward: Backward movement boundary for Alt+B
    find_path_word_end_forward: Forward movement boundary for Alt+F
"""

from .cut_backward import find_path_word_start_backward
from .move_backward import find_path_component_start_backward
from .move_forward import find_path_word_end_forward

__all__ = [
    "find_path_word_start_backward",
    "find_path_component_start_backward",
    "find_path_word_end_forward",
]
