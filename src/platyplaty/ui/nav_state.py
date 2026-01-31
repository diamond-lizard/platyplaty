"""Navigation state model for the file browser.

Provides NavigationState class for tracking current directory, selection,
scroll positions, and per-directory memory. Implementation split across
nav_* modules.
"""

from pathlib import Path

from platyplaty.ui.directory_types import DirectoryEntry, DirectoryListing
from platyplaty.ui.nav_left import move_left as _move_left
from platyplaty.ui.nav_listing import get_listing as _get_listing
from platyplaty.ui.nav_listing import get_selected_entry as _get_selected_entry
from platyplaty.ui.nav_listing import refresh_listing as _refresh_listing
from platyplaty.ui.nav_memory import set_initial_selection as _set_initial_selection
from platyplaty.ui.nav_memory_query import (
    get_parent_scroll_offset as _get_parent_scroll_offset,
)
from platyplaty.ui.nav_memory_query import (
    get_scroll_offset_for_directory as _get_scroll_offset_for_directory,
)
from platyplaty.ui.nav_memory_query import (
    get_selected_name_for_directory as _get_selected_name_for_directory,
)
from platyplaty.ui.nav_moves import move_down as _move_down
from platyplaty.ui.nav_moves import move_up as _move_up
from platyplaty.ui.nav_refresh import refresh_after_editor as _refresh_after_editor
from platyplaty.ui.nav_right import move_right as _move_right
from platyplaty.ui.nav_scroll import adjust_scroll as _adjust_scroll
from platyplaty.ui.nav_types import DirectoryMemory


class NavigationState:
    """Tracks navigation state for the file browser.

    Manages current directory, selected item, scroll positions, and
    per-directory memory of selections.
    """

    current_dir: Path
    selected_name: str | None
    scroll_offset: int
    _directory_memory: dict[str, DirectoryMemory]
    _listing: DirectoryListing | None

    def __init__(self, starting_dir: Path) -> None:
        """Initialize navigation state.

        Args:
            starting_dir: The initial directory (as logical path).
        """
        self.current_dir = starting_dir
        self._directory_memory = {}
        self._listing = None
        self.scroll_offset = 0
        _refresh_listing(self)
        _set_initial_selection(self)

    def move_up(self) -> bool:
        """Move selection up by one item."""
        return _move_up(self)

    def move_down(self) -> bool:
        """Move selection down by one item."""
        return _move_down(self)

    def move_left(self) -> bool:
        """Navigate to parent directory."""
        return _move_left(self)

    def move_right(self) -> str | None:
        """Navigate into selected directory or return file path for editor."""
        return _move_right(self)

    def get_listing(self) -> DirectoryListing | None:
        """Get the current directory listing."""
        return _get_listing(self)

    def get_selected_entry(self) -> DirectoryEntry | None:
        """Get the currently selected entry."""
        return _get_selected_entry(self)

    def refresh_after_editor(self) -> None:
        """Refresh directory after editor exits and restore selection."""
        _refresh_after_editor(self)

    def adjust_scroll(self, pane_height: int) -> None:
        """Adjust scroll_offset so the selected item is visible."""
        _adjust_scroll(self, pane_height)

    def get_parent_scroll_offset(self) -> int:
        """Get the remembered scroll offset for the parent directory."""
        return _get_parent_scroll_offset(self, self.current_dir)

    def get_selected_name_for_directory(self, directory_path: str) -> str | None:
        """Get the remembered selected name for a directory."""
        return _get_selected_name_for_directory(self, directory_path)

    def get_scroll_offset_for_directory(self, directory_path: str) -> int:
        """Get the remembered scroll offset for a directory."""
        return _get_scroll_offset_for_directory(self, directory_path)
