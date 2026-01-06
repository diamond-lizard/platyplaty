"""UI components for the Platyplaty file browser.

This package provides widgets for the three-pane file browser interface.
"""

from platyplaty.ui.directory import (
    DirectoryEntry,
    DirectoryListing,
    EntryType,
    list_directory,
)
from platyplaty.ui.file_browser import FileBrowser
from platyplaty.ui.layout import PaneWidths, calculate_pane_widths
from platyplaty.ui.pane import Pane

__all__ = [
    "DirectoryEntry",
    "DirectoryListing",
    "EntryType",
    "FileBrowser",
    "Pane",
    "PaneWidths",
    "calculate_pane_widths",
    "list_directory",
]
