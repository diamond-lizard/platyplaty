"""Pane widget for the three-pane file browser.

This module provides a Pane widget that displays a list of directory
entries, one per line, left-justified within a constrained width. See also:
pane_rendering.py for rendering helpers and pane_selection.py for
selection helpers.
"""

from textual.geometry import Size
from textual.strip import Strip
from textual.widget import Widget

from platyplaty.ui.directory_types import DirectoryEntry
from platyplaty.ui.pane_rendering import render_empty_message, render_entry


class Pane(Widget):
    """A pane widget displaying a list of directory entries.

    The pane renders entries left-justified, one per line, constrained
    to a specified width. It tracks which item is currently selected
    for later highlighting phases.

    Attributes:
        entries: List of directory entries to display.
        selected_index: Index of the currently selected entry.
        is_truly_empty: True if directory had no entries at all.
    """

    entries: list[DirectoryEntry]
    selected_index: int
    is_truly_empty: bool

    def __init__(
        self,
        entries: list[DirectoryEntry],
        width: int,
        is_truly_empty: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize the Pane widget.

        Args:
            entries: List of directory entries to display.
            width: Width to constrain rendering to, in characters.
            is_truly_empty: True if directory had no entries at all,
                False if entries were filtered out.
            name: Optional widget name.
            id: Optional widget ID.
            classes: Optional CSS classes.
        """
        super().__init__(name=name, id=id, classes=classes)
        self.entries = entries
        self._width = width
        self.is_truly_empty = is_truly_empty
        self.selected_index = 0 if entries else -1

    def render_line(self, y: int) -> Strip:
        """Render a single line of the pane.

        Args:
            y: The line number to render (0-indexed).

        Returns:
            A Strip containing the rendered line.
        """
        if not self.entries:
            return render_empty_message(
                y, self.is_truly_empty, self._width, self.app.console
            )
        if y < len(self.entries):
            return render_entry(
                self.entries[y], self._width, self.app.console
            )
        return Strip([])

    def get_content_height(
        self, container: "Size", viewport: "Size", width: int
    ) -> int:
        """Return the height of the content.

        Args:
            container: Size of the container.
            viewport: Size of the viewport.
            width: Width available.

        Returns:
            Number of lines needed to display content.
        """
        if not self.entries:
            return 1  # One line for empty message
        return len(self.entries)

