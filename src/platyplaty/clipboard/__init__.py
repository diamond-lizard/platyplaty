"""Clipboard access module for platyplaty.

Provides functions for reading clipboard and selection content.
"""

from platyplaty.clipboard.x11_selection import get_primary_selection

__all__ = ["get_primary_selection"]
