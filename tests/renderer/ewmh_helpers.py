#!/usr/bin/env python3
"""
EWMH helpers for window close testing.

Provides utilities for closing windows via the EWMH protocol.
"""

try:
    from ewmh import EWMH
    EWMH_AVAILABLE = True
except ImportError:
    EWMH_AVAILABLE = False


def _try_close_window(ewmh, win, window_name: str) -> bool:
    """Try to close a single window if it matches the target name.

    Returns True if window was closed, False otherwise.
    """
    if win is None:
        return False
    try:
        wm_name = win.get_wm_name()
    except Exception:
        return False
    if not wm_name or window_name not in wm_name:
        return False
    ewmh.setCloseWindow(win)
    ewmh.display.flush()
    return True


def close_window_by_name(window_name: str) -> bool:
    """Close a window by name using EWMH protocol.

    Args:
        window_name: The window title to search for.

    Returns:
        True if window was found and close request sent, False otherwise.
    """
    if not EWMH_AVAILABLE:
        return False

    ewmh = EWMH()
    for win in ewmh.getClientList():
        if _try_close_window(ewmh, win, window_name):
            return True
    return False
