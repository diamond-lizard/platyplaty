"""Navigation state model for the file browser.

This module provides the NavigationState class that tracks the current
directory, selected item, scroll positions, and handles navigation
state transitions.
"""

from dataclasses import dataclass
from pathlib import Path

from platyplaty.errors import InaccessibleDirectoryError
from platyplaty.ui.directory import (
    DirectoryEntry,
    DirectoryListing,
    EntryType,
    list_directory,
)


@dataclass
class DirectoryMemory:
    """Remembered state for a directory.

    Attributes:
        selected_name: The name of the selected item.
        scroll_offset: The scroll offset in the pane.
    """

    selected_name: str | None = None
    scroll_offset: int = 0


def _find_name_in_listing(listing: DirectoryListing, name: str) -> bool:
    """Check if a name exists in a directory listing.

    Args:
        listing: The directory listing to search.
        name: The name to find.

    Returns:
        True if the name exists in the listing.
    """
    return any(entry.name == name for entry in listing.entries)


def _find_index_by_name(listing: DirectoryListing, name: str) -> int | None:
    """Find the index of an entry by name.

    Args:
        listing: The directory listing to search.
        name: The name to find.

    Returns:
        The index of the entry, or None if not found.
    """
    for i, entry in enumerate(listing.entries):
        if entry.name == name:
            return i
    return None


class NavigationState:
    """Tracks navigation state for the file browser.

    This class manages the current directory (as a logical path preserving
    symlink traversal), selected item, and per-directory memory of
    selections and scroll positions.

    Attributes:
        current_dir: The current directory as a logical Path.
        selected_name: The name of the currently selected item.
        scroll_offset: The current scroll offset in the middle pane.
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
        self._refresh_listing()
        self._set_initial_selection()

    def _set_initial_selection(self) -> None:
        """Set selection to first item or None if empty."""
        if not self._listing or not self._listing.entries:
            self.selected_name = None
            return
        self.selected_name = self._listing.entries[0].name

    def _refresh_listing(self) -> None:
        """Refresh the directory listing for the current directory."""
        self._listing = list_directory(self.current_dir)

    def _get_selected_index(self) -> int | None:
        """Get the index of the currently selected item.

        Returns:
            The index of the selected item, or None if no selection.
        """
        if not self._listing or not self._listing.entries:
            return None
        if self.selected_name is None:
            return None
        return _find_index_by_name(self._listing, self.selected_name)

    def _is_empty_or_inaccessible(self) -> bool:
        """Check if current directory is empty or inaccessible.

        Returns:
            True if the directory is empty or inaccessible.
        """
        if not self._listing:
            return True
        if self._listing.permission_denied:
            return True
        return len(self._listing.entries) == 0

    def _save_current_memory(self) -> None:
        """Save current selection and scroll position to directory memory."""
        key = str(self.current_dir)
        self._directory_memory[key] = DirectoryMemory(
            selected_name=self.selected_name,
            scroll_offset=self.scroll_offset,
        )

    def _try_restore_remembered_name(self, memory: DirectoryMemory) -> bool:
        """Try to restore a remembered selection.

        Args:
            memory: The directory memory to restore from.

        Returns:
            True if the remembered name was found and restored.
        """
        if not memory.selected_name:
            return False
        if not self._listing or not self._listing.entries:
            return False
        if not _find_name_in_listing(self._listing, memory.selected_name):
            return False
        self.selected_name = memory.selected_name
        self.scroll_offset = memory.scroll_offset
        return True

    def _restore_memory(self) -> None:
        """Restore selection and scroll position from directory memory."""
        key = str(self.current_dir)
        memory = self._directory_memory.get(key)
        if memory and self._try_restore_remembered_name(memory):
            return
        self._set_initial_selection()
        self.scroll_offset = 0

    def move_up(self) -> bool:
        """Move selection up by one item.

        No-op if directory is empty or inaccessible, or already at top.

        Returns:
            True if selection moved, False otherwise.
        """
        if self._is_empty_or_inaccessible():
            return False
        assert self._listing is not None  # narrowed by _is_empty_or_inaccessible
        index = self._get_selected_index()
        if index is None or index <= 0:
            return False
        self.selected_name = self._listing.entries[index - 1].name
        return True

    def move_down(self) -> bool:
        """Move selection down by one item.

        No-op if directory is empty or inaccessible, or already at bottom.

        Returns:
            True if selection moved, False otherwise.
        """
        if self._is_empty_or_inaccessible():
            return False
        assert self._listing is not None  # narrowed by _is_empty_or_inaccessible
        index = self._get_selected_index()
        if index is None:
            return False
        max_index = len(self._listing.entries) - 1
        if index >= max_index:
            return False
        self.selected_name = self._listing.entries[index + 1].name
        return True

    def move_left(self) -> bool:
        """Navigate to parent directory.

        No-op if at filesystem root. Saves current memory before navigating.

        Returns:
            True if navigated, False if at root.

        Raises:
            InaccessibleDirectoryError: If parent directory cannot be accessed.
        """
        parent = self.current_dir.parent
        if parent == self.current_dir:
            return False
        # Check if parent is accessible before navigating
        try:
            list(parent.iterdir())
        except PermissionError:
            raise InaccessibleDirectoryError(str(parent)) from None
        except OSError:
            raise InaccessibleDirectoryError(str(parent)) from None
        self._save_current_memory()
        came_from = self.current_dir.name
        self.current_dir = parent
        self._refresh_listing()
        self.selected_name = came_from
        self._restore_scroll_from_memory()
        return True

    def _restore_scroll_from_memory(self) -> None:
        """Restore scroll offset from directory memory if available."""
        key = str(self.current_dir)
        memory = self._directory_memory.get(key)
        if memory:
            self.scroll_offset = memory.scroll_offset
            return
        self.scroll_offset = 0

    def move_right(self) -> str | None:
        """Navigate into selected directory or return file path for editor.

        For directories and symlinks to directories: navigates into them.
        For files and symlinks to files: returns the path for editor.
        For broken symlinks: no-op.
        No-op if directory is empty or inaccessible.

        Returns:
            Path string if a file should be opened in editor, None otherwise.

        Raises:
            InaccessibleDirectoryError: If target directory cannot be accessed.
        """
        if self._is_empty_or_inaccessible():
            return None
        entry = self.get_selected_entry()
        if entry is None:
            return None
        return self._handle_move_right_entry(entry)

    def _handle_move_right_entry(self, entry: DirectoryEntry) -> str | None:
        """Handle move_right for a specific entry type.

        Args:
            entry: The selected directory entry.

        Returns:
            Path string if a file should be opened in editor, None otherwise.
        """
        if entry.entry_type == EntryType.BROKEN_SYMLINK:
            return None
        if entry.entry_type in (EntryType.FILE, EntryType.SYMLINK_TO_FILE):
            return str(self.current_dir / entry.name)
        if entry.entry_type in (EntryType.DIRECTORY, EntryType.SYMLINK_TO_DIRECTORY):
            self._navigate_into_directory(entry.name)
        return None

    def _navigate_into_directory(self, name: str) -> None:
        """Navigate into a subdirectory.

        Args:
            name: The name of the directory to enter.

        Raises:
            InaccessibleDirectoryError: If target directory cannot be accessed.
        """
        target = self.current_dir / name
        # Check if target is accessible before navigating
        try:
            list(target.iterdir())
        except PermissionError:
            raise InaccessibleDirectoryError(str(target)) from None
        except OSError:
            raise InaccessibleDirectoryError(str(target)) from None
        self._save_current_memory()
        self.current_dir = self.current_dir / name
        self._refresh_listing()
        self._restore_memory()

    def get_listing(self) -> DirectoryListing | None:
        """Get the current directory listing.

        Returns:
            The DirectoryListing for the current directory.
        """
        return self._listing

    def get_selected_entry(self) -> DirectoryEntry | None:
        """Get the currently selected entry.

        Returns:
            The selected DirectoryEntry, or None if no selection.
        """
        index = self._get_selected_index()
        if index is None or not self._listing:
            return None
        return self._listing.entries[index]

    def refresh_after_editor(self) -> None:
        """Refresh directory after editor exits and restore selection.

        Re-reads the current directory listing. If the previously selected
        filename still exists, keeps it selected. Otherwise, selects the
        item that is now at the previous index position (or the last item
        if the previous position is beyond the new list length).
        """
        old_name = self.selected_name
        old_index = self._get_selected_index()
        self._refresh_listing()

        # Try to keep the same filename selected
        if (old_name and self._listing and self._listing.entries
                and _find_name_in_listing(self._listing, old_name)):
            return  # Name still exists, keep it

        # Filename gone: select item at previous index, or last item
        if self._listing and self._listing.entries:
            max_index = len(self._listing.entries) - 1
            if old_index is not None and old_index <= max_index:
                self.selected_name = self._listing.entries[old_index].name
            else:
                self.selected_name = self._listing.entries[max_index].name
        else:
            self.selected_name = None

    def adjust_scroll(self, pane_height: int) -> None:
        """Adjust scroll_offset so the selected item is visible.

        Call this after any operation that changes selection to ensure
        the selected item remains visible within the pane.

        Args:
            pane_height: The height of the pane in lines. If zero or
                negative, this method does nothing.
        """
        if pane_height <= 0:
            return
        selected_index = self._get_selected_index()
        if selected_index is None:
            return
        self._clamp_scroll_to_selection(selected_index, pane_height)

    def _clamp_scroll_to_selection(self, index: int, pane_height: int) -> None:
        """Clamp scroll_offset so index is visible within pane_height.

        Args:
            index: The selected item index.
            pane_height: The height of the pane in lines.
        """
        if index < self.scroll_offset:
            self.scroll_offset = index
            return
        visible_end = self.scroll_offset + pane_height
        if index >= visible_end:
            self.scroll_offset = index - pane_height + 1
