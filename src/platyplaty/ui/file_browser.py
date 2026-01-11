"""File browser widget with three-pane layout.

Implementation split across: file_browser_init, file_browser_render,
file_browser_refresh, file_browser_sync, file_browser_nav,
file_browser_nav_updown, file_browser_error, file_browser_key.
"""

from pathlib import Path

from textual.events import Key, Resize
from textual.geometry import Size
from textual.strip import Strip
from textual.widget import Widget

from platyplaty.dispatch_tables import DispatchTable
from platyplaty.ui.directory_types import DirectoryEntry, DirectoryListing
from platyplaty.ui.file_browser_init import init_browser as _init_browser
from platyplaty.ui.file_browser_key import on_key as _on_key
from platyplaty.ui.file_browser_render import render_line as _render_line
from platyplaty.ui.file_browser_sync import (
    adjust_left_pane_scroll as _adjust_left_scroll,
    adjust_right_pane_scroll as _adjust_right_scroll,
)
from platyplaty.ui.file_browser_sync import (
    refresh_panes as _refresh_panes,
)
from platyplaty.ui.file_browser_types import RightPaneContent
from platyplaty.ui.nav_state import NavigationState


class FileBrowser(Widget):
    """A three-pane file browser widget.

    Displays left (parent), middle (current), and right (preview) panes.
    """

    can_focus = True
    current_dir: Path
    selected_index: int
    _nav_state: NavigationState
    _dispatch_table: DispatchTable
    _middle_scroll_offset: int
    _left_scroll_offset: int
    _right_scroll_offset: int
    _left_listing: DirectoryListing | None
    _middle_listing: DirectoryListing | None
    _right_content: RightPaneContent
    _right_selected_index: int | None

    def __init__(
        self,
        dispatch_table: DispatchTable,
        starting_dir: Path | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize the FileBrowser widget."""
        super().__init__(name=name, id=id, classes=classes)
        _init_browser(self, dispatch_table, starting_dir)

    def get_content_width(self, container: Size, viewport: Size) -> int:
        """Return the content width."""
        return container.width

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        """Return the content height."""
        return container.height

    def render_line(self, y: int) -> Strip:
        """Render a single line of the file browser."""
        return _render_line(self, y)

    def on_resize(self, event: Resize) -> None:
        """Handle terminal resize events."""
        _adjust_left_scroll(self, self.size.height - 1)
        _adjust_right_scroll(self, self.size.height - 1)
        self.refresh()

    def on_mount(self) -> None:
        """Handle mount event to adjust scroll when size becomes valid."""
        _adjust_left_scroll(self, self.size.height - 1)
        _adjust_right_scroll(self, self.size.height - 1)

    def get_selected_entry(self) -> DirectoryEntry | None:
        """Get the currently selected entry."""
        if not self._middle_listing or not self._middle_listing.entries:
            return None
        entries = self._middle_listing.entries
        if self.selected_index < 0 or self.selected_index >= len(entries):
            return None
        return self._middle_listing.entries[self.selected_index]

    def refresh_panes(self) -> None:
        """Refresh all three panes after navigation state changes."""
        _refresh_panes(self)

    async def on_key(self, event: Key) -> None:
        """Handle key events for file browser navigation."""
        await _on_key(self, event)
