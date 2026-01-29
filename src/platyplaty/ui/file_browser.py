"""File browser widget with three-pane layout.

Implementation split across: file_browser_init, file_browser_render,
file_browser_refresh, file_browser_sync, file_browser_nav,
file_browser_nav_updown, file_browser_error, file_browser_key.
"""

from pathlib import Path
from typing import TYPE_CHECKING

from textual.events import Key, Resize
from textual.geometry import Size
from textual.strip import Strip
from textual.widget import Widget

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp

from platyplaty.dispatch_tables import DispatchTable
from platyplaty.ui.directory_types import DirectoryEntry, DirectoryListing
from platyplaty.ui.file_browser_init import init_browser as _init_browser
from platyplaty.ui.file_browser_key import on_key as _on_key
from platyplaty.ui.file_browser_render import render_line as _render_line
from platyplaty.ui.file_browser_refresh import (
    refresh_right_pane as _refresh_right_pane,
)
from platyplaty.ui.file_browser_scroll import (
    adjust_left_pane_scroll as _adjust_left_scroll,
)
from platyplaty.ui.file_browser_scroll import (
    adjust_middle_pane_scroll as _adjust_middle_scroll,
)
from platyplaty.ui.file_browser_scroll import (
    adjust_right_pane_scroll as _adjust_right_scroll,
)
from platyplaty.ui.file_browser_sync import (
    get_selected_entry as _get_selected_entry,
)
from platyplaty.ui.file_browser_sync import (
    refresh_panes as _refresh_panes,
)
from platyplaty.ui.file_browser_types import RightPaneContent
from platyplaty.ui.layout_state import LayoutState
from platyplaty.ui.nav_state import NavigationState


class FileBrowser(Widget):
    """A three-pane file browser widget.

    Displays left (parent), middle (current), and right (preview) panes.
    """

    can_focus = True
    current_dir: Path
    _nav_state: NavigationState
    _dispatch_table: DispatchTable
    _middle_scroll_offset: int
    _left_scroll_offset: int
    _right_scroll_offset: int
    _left_listing: DirectoryListing | None
    _middle_listing: DirectoryListing | None
    _right_content: RightPaneContent
    _right_selected_index: int | None
    _layout_state: LayoutState


    @property
    def platyplaty_app(self) -> "PlatyplatyApp":
        """Return the app instance typed as PlatyplatyApp."""
        from platyplaty.app import PlatyplatyApp
        assert isinstance(self.app, PlatyplatyApp)
        return self.app

    def __init__(
        self,
        dispatch_table: DispatchTable,
        starting_dir: Path | None = None,
        focused: bool = False,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize the FileBrowser widget."""
        super().__init__(name=name, id=id, classes=classes)
        _init_browser(self, dispatch_table, starting_dir, focused)

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
        _refresh_right_pane(self)
        _adjust_left_scroll(self, self.size.height - 1)
        _adjust_right_scroll(self, self.size.height - 1)
        _adjust_middle_scroll(self, self.size.height - 1)
        self.refresh()

    def on_mount(self) -> None:
        """Handle mount event to adjust scroll when size becomes valid."""
        _adjust_left_scroll(self, self.size.height - 1)
        _adjust_right_scroll(self, self.size.height - 1)

    def get_selected_entry(self) -> DirectoryEntry | None:
        """Get the currently selected entry."""
        return _get_selected_entry(self)

    def refresh_panes(self) -> None:
        """Refresh all three panes after navigation state changes."""
        _refresh_panes(self)

    def set_focused(self, focused: bool) -> None:
        """Set whether this widget is focused."""
        self._focused = focused
        self.refresh()

    async def on_key(self, event: Key) -> None:
        """Handle key events for file browser navigation."""
        await _on_key(self, event)

    @property
    def selected_index(self) -> int | None:
        """Get the index of the currently selected item.

        This is derived from _nav_state.selected_name to ensure
        the browser and navigation state are always in sync.

        Returns:
            The index of the selected item, or None if no selection.
        """
        if not hasattr(self, '_nav_state'):
            return None
        listing = self._nav_state.get_listing()
        if listing is None or not listing.entries:
            return None
        name = self._nav_state.selected_name
        if name is None:
            return None
        for i, entry in enumerate(listing.entries):
            if entry.name == name:
                return i
        return None

    def set_selection_by_index(self, index: int) -> None:
        """Set the selection by index.

        Updates _nav_state.selected_name to the name at the given index.
        This is the only way to change the selection by index.

        Args:
            index: The index of the item to select.
        """
        listing = self._nav_state.get_listing()
        if listing is None or not listing.entries:
            return
        if index < 0 or index >= len(listing.entries):
            return
        self._nav_state.selected_name = listing.entries[index].name
