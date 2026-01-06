"""File browser container widget with three-pane layout.

This module provides the FileBrowser widget that composes three Pane
widgets horizontally: left (parent directory), middle (current directory),
and right (preview of selected item).
"""

from pathlib import Path

from textual.widget import Widget
from textual.strip import Strip
from textual.geometry import Size

from platyplaty.ui.layout import calculate_pane_widths
from platyplaty.ui.directory import (
    DirectoryEntry,
    DirectoryListing,
    EntryType,
    list_directory,
)
from platyplaty.ui.pane import Pane
from platyplaty.errors import InaccessibleDirectoryError


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

    def __init__(
        self,
        starting_dir: Path | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize the FileBrowser widget.

        Args:
            starting_dir: Initial directory to display. Defaults to CWD.
            name: Optional widget name.
            id: Optional widget ID.
            classes: Optional CSS classes.
        """
        super().__init__(name=name, id=id, classes=classes)
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

        # Cache for directory listings
        self._left_listing: DirectoryListing | None = None
        self._middle_listing: DirectoryListing | None = None
        self._right_listing: DirectoryListing | None = None

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
            self._right_listing = None
            return

        if self.selected_index < 0 or self.selected_index >= len(self._middle_listing.entries):
            self._right_listing = None
            return

        selected = self._middle_listing.entries[self.selected_index]

        # Only show directory contents for directories
        if selected.entry_type in (EntryType.DIRECTORY, EntryType.SYMLINK_TO_DIRECTORY):
            selected_path = self.current_dir / selected.name
            self._right_listing = list_directory(selected_path)
        else:
            # File selected - right pane empty (file preview deferred)
            self._right_listing = None

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
            self._middle_listing, y, pane_widths.middle, is_left_pane=False
        )
        segments.append(Segment(middle_text))
        segments.append(Segment(" "))  # Gap

        # Render right pane
        right_text = self._render_pane_line(
            self._right_listing, y, pane_widths.right, is_left_pane=False
        )
        segments.append(Segment(right_text))

        return Strip(segments)

    def _render_pane_line(
        self,
        listing: DirectoryListing | None,
        y: int,
        width: int,
        is_left_pane: bool,
    ) -> str:
        """Render a single line of a pane.

        Args:
            listing: The directory listing to render.
            y: The line number to render (0-indexed).
            width: The width of the pane.
            is_left_pane: True if rendering the left pane (for root case).

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
                if listing.was_empty:
                    msg = "empty"
                else:
                    msg = "no .milk files"
                return msg.ljust(width)[:width]
            return " " * width

        # Render entry
        if y < len(listing.entries):
            name = listing.entries[y].name
            return name.ljust(width)[:width]

        return " " * width

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
