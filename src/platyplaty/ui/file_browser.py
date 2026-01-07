"""File browser container widget with three-pane layout.

This module provides the FileBrowser widget that composes three Pane
widgets horizontally: left (parent directory), middle (current directory),
and right (preview of selected item).
"""

from pathlib import Path
from dataclasses import dataclass

from textual.widget import Widget
from textual.strip import Strip
from textual.geometry import Size
from textual.events import Key

from platyplaty.ui.layout import calculate_pane_widths
from platyplaty.ui.directory import (
    DirectoryEntry,
    DirectoryListing,
    EntryType,
    list_directory,
)
from platyplaty.ui.pane import Pane
from platyplaty.errors import InaccessibleDirectoryError
from platyplaty.errors import NoEditorFoundError
from platyplaty.ui.nav_state import NavigationState
from platyplaty.ui.editor import open_in_editor
from platyplaty.keybinding_dispatch import DispatchTable


@dataclass
class RightPaneDirectory:
    """Right pane content showing a directory listing."""

    listing: DirectoryListing


@dataclass
class RightPaneFilePreview:
    """Right pane content showing lines from a file."""

    lines: tuple[str, ...]


RightPaneContent = RightPaneDirectory | RightPaneFilePreview | None


def read_file_preview_lines(path: Path) -> tuple[str, ...] | None:
    """Read lines from a file for preview.

    Args:
        path: Path to the file to read.

    Returns:
        Tuple of lines from the file, or None if file cannot be read.
    """
    try:
        with path.open('r', encoding='utf-8', errors='replace') as f:
            return tuple(f.readlines())
    except (OSError, IOError):
        return None


class FileBrowser(Widget):
    """A three-pane file browser widget.

    Displays three horizontal panes:
    - Left: Parent directory contents (siblings of current directory)
    - Middle: Current directory contents
    - Right: Preview of selected item (directory listing or empty for files)

    Attributes:
        current_dir: Path to the current directory.
        selected_index: Index of the selected item in middle pane.
    """

    current_dir: Path
    selected_index: int
    _nav_state: NavigationState
    _dispatch_table: DispatchTable
    _middle_scroll_offset: int

    def __init__(
        self,
        dispatch_table: DispatchTable,
        starting_dir: Path | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize the FileBrowser widget.

        Args:
            dispatch_table: Dispatch table for navigation key bindings.
            starting_dir: Initial directory to display. Defaults to CWD.
            name: Optional widget name.
            id: Optional widget ID.
            classes: Optional CSS classes.
        """
        super().__init__(name=name, id=id, classes=classes)
        self._dispatch_table = dispatch_table
        if starting_dir is None:
            self.current_dir = Path.cwd()
        else:
            self.current_dir = starting_dir.resolve()

        # Check if directory is accessible
        if not self.current_dir.is_dir():
            raise InaccessibleDirectoryError(str(self.current_dir))
        try:
            list(self.current_dir.iterdir())
        except PermissionError:
            raise InaccessibleDirectoryError(str(self.current_dir))
        self.selected_index = 0
        self._middle_scroll_offset = 0

        # Cache for directory listings
        self._left_listing: DirectoryListing | None = None
        self._middle_listing: DirectoryListing | None = None
        self._right_content: RightPaneContent = None

        # Navigation state manager
        self._nav_state = NavigationState(self.current_dir)

        # Refresh listings on init
        self._refresh_listings()

    def _refresh_listings(self) -> None:
        """Refresh all directory listings based on current state."""
        # Middle pane: current directory
        self._middle_listing = list_directory(self.current_dir)

        # Left pane: parent directory (empty at filesystem root)
        parent = self.current_dir.parent
        if parent == self.current_dir:
            # At filesystem root
            self._left_listing = DirectoryListing(
                entries=[],
                was_empty=True,
                had_filtered_entries=False,
                permission_denied=False,
            )
        else:
            self._left_listing = list_directory(parent)

        # Right pane: preview of selected item
        self._refresh_right_pane()

    def _refresh_right_pane(self) -> None:
        """Refresh the right pane based on selected item."""
        if not self._middle_listing or not self._middle_listing.entries:
            self._right_content = None
            return

        if self.selected_index < 0 or self.selected_index >= len(self._middle_listing.entries):
            self._right_content = None
            return

        selected = self._middle_listing.entries[self.selected_index]

        # Only show directory contents for directories
        if selected.entry_type in (EntryType.DIRECTORY, EntryType.SYMLINK_TO_DIRECTORY):
            selected_path = self.current_dir / selected.name
            self._right_content = RightPaneDirectory(list_directory(selected_path))
        else:
            # File selected - show file preview
            self._right_content = self._make_file_preview(selected)

    def _make_file_preview(self, entry: DirectoryEntry) -> RightPaneContent:
        """Create file preview content for an entry.

        Args:
            entry: The directory entry to preview.

        Returns:
            RightPaneFilePreview with file lines, or None if unreadable.
        """
        file_path = self.current_dir / entry.name
        lines = read_file_preview_lines(file_path)
        if lines is None:
            return None
        return RightPaneFilePreview(lines)

    def get_content_width(self, container: Size, viewport: Size) -> int:
        """Return the content width.

        Args:
            container: Size of the container.
            viewport: Size of the viewport.

        Returns:
            The full container width.
        """
        return container.width

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        """Return the content height.

        Args:
            container: Size of the container.
            viewport: Size of the viewport.
            width: Width available.

        Returns:
            The full container height.
        """
        return container.height

    def render_line(self, y: int) -> Strip:
        """Render a single line of the file browser.

        Args:
            y: The line number to render (0-indexed).

        Returns:
            A Strip containing the rendered line.
        """
        from rich.text import Text
        from rich.segment import Segment

        width = self.size.width
        pane_widths = calculate_pane_widths(width)

        segments: list[Segment] = []

        # Render left pane
        if pane_widths.left > 0:
            left_text = self._render_pane_line(
                self._left_listing, y, pane_widths.left, is_left_pane=True
            )
            segments.append(Segment(left_text))
            segments.append(Segment(" "))  # Gap

        # Render middle pane
        middle_text = self._render_pane_line(
            self._middle_listing, y, pane_widths.middle, is_left_pane=False, scroll_offset=self._middle_scroll_offset
        )
        segments.append(Segment(middle_text))
        segments.append(Segment(" "))  # Gap

        # Render right pane
        right_text = self._render_right_pane_line(y, pane_widths.right)
        segments.append(Segment(right_text))

        return Strip(segments)

    def _render_pane_line(
        self,
        listing: DirectoryListing | None,
        y: int,
        width: int,
        is_left_pane: bool,
        scroll_offset: int = 0,
    ) -> str:
        """Render a single line of a pane.

        Args:
            listing: The directory listing to render.
            y: The line number to render (0-indexed).
            width: The width of the pane.
            is_left_pane: True if rendering the left pane (for root case).
            scroll_offset: Offset into the listing for scrolling (default 0).

        Returns:
            A string padded to the pane width.
        """
        if listing is None:
            return " " * width

        # Handle empty listing
        if not listing.entries:
            if is_left_pane and listing.was_empty:
                # At filesystem root - left pane is truly empty
                return " " * width
            if y == 0:
                if listing.permission_denied:
                    msg = "inaccessible directory"
                elif listing.was_empty:
                    msg = "empty"
                else:
                    msg = "no .milk files"
                return msg.ljust(width)[:width]
            return " " * width

        # Render entry
        if y + scroll_offset < len(listing.entries):
            name = listing.entries[y + scroll_offset].name
            return name.ljust(width)[:width]

        return " " * width

    def _render_right_pane_line(self, y: int, width: int) -> str:
        """Render a single line of the right pane.

        Handles both directory listings and file previews.

        Args:
            y: The line number to render (0-indexed).
            width: The width of the pane.

        Returns:
            A string padded to the pane width.
        """
        content = self._right_content
        if content is None:
            return " " * width
        if isinstance(content, RightPaneDirectory):
            return self._render_pane_line(content.listing, y, width, is_left_pane=False)
        return self._render_file_preview_line(content.lines, y, width)

    def _render_file_preview_line(
        self, lines: tuple[str, ...], y: int, width: int
    ) -> str:
        """Render a single line of file preview.

        Args:
            lines: The file lines to display.
            y: The line number to render (0-indexed).
            width: The width of the pane.

        Returns:
            A string padded/truncated to the pane width.
        """
        if y >= len(lines):
            return " " * width
        line = lines[y].rstrip('\n\r')
        return line.ljust(width)[:width]

    def on_resize(self, event) -> None:
        """Handle terminal resize events.

        Args:
            event: The resize event.
        """
        self.refresh()

    def get_selected_entry(self) -> DirectoryEntry | None:
        """Get the currently selected entry.

        Returns:
            The selected DirectoryEntry, or None if no entries.
        """
        if not self._middle_listing or not self._middle_listing.entries:
            return None
        if self.selected_index < 0 or self.selected_index >= len(self._middle_listing.entries):
            return None
        return self._middle_listing.entries[self.selected_index]

    def _find_entry_index(self, listing: DirectoryListing, name: str) -> int:
        """Find the index of an entry by name.

        Args:
            listing: The directory listing to search.
            name: The name to find.

        Returns:
            Index of the entry, or 0 if not found.
        """
        gen = (i for i, e in enumerate(listing.entries) if e.name == name)
        return next(gen, 0)

    def _sync_from_nav_state(self) -> None:
        """Sync FileBrowser state from NavigationState.

        Updates current_dir, selected_index, and scroll offset from nav state.
        """
        self.current_dir = self._nav_state.current_dir
        listing = self._nav_state.get_listing()
        if listing is None or not listing.entries:
            self.selected_index = 0
            return
        selected_entry = self._nav_state.get_selected_entry()
        if selected_entry is None:
            self.selected_index = 0
            return
        self.selected_index = self._find_entry_index(listing, selected_entry.name)
        self._nav_state.adjust_scroll(self.size.height)
        self._middle_scroll_offset = self._nav_state.scroll_offset

    def refresh_panes(self) -> None:
        """Refresh all three panes after navigation state changes.

        This method syncs state from NavigationState, refreshes all
        directory listings, and triggers a visual refresh. It should
        be called after any navigation action that changes pane contents.
        """
        self._sync_from_nav_state()
        self._refresh_listings()
        self.refresh()

    def _show_transient_error(self, message: str) -> None:
        """Show a transient error message at the bottom of the screen.

        Displays black text on red background for 0.5 seconds.

        Args:
            message: The error message to display.
        """
        # TODO: Implement transient error display (Phase 60 or later)
        pass

    async def _open_in_editor(self, file_path: str) -> None:
        """Open a file in the external editor.

        Suspends the app, runs the editor, then refreshes after exit.

        Args:
            file_path: Path to the file to edit.

        Raises:
            NoEditorFoundError: If no editor is available.
        """
        await open_in_editor(self.app, file_path)
        self._nav_state.refresh_after_editor()
        self._sync_from_nav_state()
        self._refresh_listings()
        self.refresh()

    async def action_nav_up(self) -> None:
        """Move selection up in the current directory.

        No-op if already at top, directory is empty, or inaccessible.
        """
        if not self._nav_state.move_up():
            return
        self._sync_from_nav_state()
        self._refresh_right_pane()
        self.refresh()

    async def action_nav_down(self) -> None:
        """Move selection down in the current directory.

        No-op if already at bottom, directory is empty, or inaccessible.
        """
        if not self._nav_state.move_down():
            return
        self._sync_from_nav_state()
        self._refresh_right_pane()
        self.refresh()

    async def action_nav_left(self) -> None:
        """Navigate to parent directory.

        No-op if at filesystem root. Shows error if parent inaccessible.
        """
        try:
            moved = self._nav_state.move_left()
        except InaccessibleDirectoryError:
            self._show_transient_error("permission denied")
            return
        if not moved:
            return
        self.refresh_panes()

    async def action_nav_right(self) -> None:
        """Navigate into directory or open file in editor.

        For directories: navigates into them.
        For files: opens in external editor.
        For broken symlinks: no-op.
        Shows error if directory inaccessible or no editor found.
        """
        file_path = self._handle_nav_right()
        if file_path is None:
            return
        await self._open_in_editor(file_path)

    def _handle_nav_right(self) -> str | None:
        """Handle right navigation, returning file path if editor needed.

        Returns:
            File path string if a file should be opened, None otherwise.
        """
        try:
            file_path = self._nav_state.move_right()
        except InaccessibleDirectoryError:
            self._show_transient_error("permission denied")
            return None
        if file_path is not None:
            return file_path
        self.refresh_panes()
        return None

    async def on_key(self, event: Key) -> None:
        """Handle key events for file browser navigation.

        Looks up the key in the dispatch table and calls the action method.

        Args:
            event: The key event from Textual.
        """
        if not self.has_focus:
            return
        action_name = self._dispatch_table.get(event.key)
        if action_name is None:
            return
        action_method = getattr(self, f"action_{action_name}", None)
        if action_method is not None:
            await action_method()
            event.prevent_default()
