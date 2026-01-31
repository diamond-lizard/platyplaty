#!/usr/bin/env python3
"""X11 primary selection access using Tkinter.

This module provides a simple interface for reading the X11 primary
selection (middle-click paste buffer) using Tkinter's clipboard_get
functionality.
"""


def get_primary_selection() -> str:
    """Read the X11 primary selection and return its text content.

    Uses Tkinter to access the X11 PRIMARY selection (the content that
    would be pasted with middle-click). A temporary Tk window is created
    and immediately hidden, then destroyed after reading the selection.

    Returns:
        The text content of the primary selection. Returns an empty string
        if the selection is unavailable (empty, no X11 display, or Tkinter
        not installed).

    Note:
        This function handles all expected errors gracefully:
        - TclError: Selection is empty or unavailable
        - ImportError: Tkinter is not installed
        - OSError: X11 display is not available
    """
    try:
        import tkinter as tk
    except ImportError:
        return ""

    root = None
    try:
        root = tk.Tk()
        root.withdraw()
        return root.clipboard_get(selection="PRIMARY")
    except (tk.TclError, OSError):
        return ""
    finally:
        if root is not None:
            root.destroy()
