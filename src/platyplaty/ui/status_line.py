"""Status line widget showing autoplay state and playlist filename.

The status line displays:
- Autoplay state: "[autoplay: on]" or "[autoplay: off]"
- Playlist filename (basename) or "no playlist file loaded"
- Unsaved changes indicator: "* " prefix on filename when dirty

Styled with black foreground on blue background.
"""

from pathlib import Path

from rich.segment import Segment
from rich.style import Style
from textual.strip import Strip
from textual.widget import Widget


# Styling: black foreground on blue background
STATUS_LINE_STYLE = Style(color="black", bgcolor="blue")


class StatusLine(Widget):
    """Widget displaying autoplay state and playlist filename.

    Attributes:
        _autoplay_enabled: Whether autoplay is on.
        _playlist_filename: The associated filename or None.
        _dirty: Whether the playlist has unsaved changes.
    """

    DEFAULT_CSS = """
    StatusLine {
        dock: bottom;
        height: 1;
    }
    """

    _autoplay_enabled: bool
    _playlist_filename: Path | None
    _dirty: bool

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize the StatusLine widget."""
        super().__init__(name=name, id=id, classes=classes)
        self._autoplay_enabled = False
        self._playlist_filename = None
        self._dirty = False

    def update_state(
        self,
        autoplay_enabled: bool,
        playlist_filename: Path | None,
        dirty: bool,
    ) -> None:
        """Update the status line state and refresh display.

        Args:
            autoplay_enabled: Whether autoplay is currently on.
            playlist_filename: Associated filename or None if not loaded.
            dirty: True if playlist has unsaved changes.
        """
        self._autoplay_enabled = autoplay_enabled
        self._playlist_filename = playlist_filename
        self._dirty = dirty
        self.refresh()

    def render_line(self, y: int) -> Strip:
        """Render a single line of the status bar."""
        if y != 0:
            return Strip([])
        from platyplaty.ui.status_line_render import render_status_line
        return render_status_line(self, self.size.width)
