"""Playlist view widget for displaying playlists.

Implementation split across: playlist_display_name, playlist_render.
"""

from textual.events import Resize
from textual.geometry import Size
from textual.strip import Strip
from textual.widget import Widget

from platyplaty.playlist import Playlist
from platyplaty.ui.playlist_render import render_line as _render_line


class PlaylistView(Widget):
    """Widget for displaying a playlist of presets.

    Shows preset filenames with selection and playing indicators.
    """

    can_focus = True
    _playlist: Playlist
    _scroll_offset: int
    _focused: bool
    _display_names: list[str]

    def __init__(
        self,
        playlist: Playlist,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize the PlaylistView widget."""
        super().__init__(name=name, id=id, classes=classes)
        self._playlist = playlist
        self._scroll_offset = 0
        self._focused = True
        self._display_names = []
        self._update_display_names()

    def _update_display_names(self) -> None:
        """Update cached display names for all presets."""
        from platyplaty.ui.playlist_display_name import (
            compute_display_names,
        )

        self._display_names = compute_display_names(self._playlist.presets)

    def get_content_width(self, container: Size, viewport: Size) -> int:
        """Return the content width."""
        return container.width

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        """Return the content height."""
        return container.height

    def render_line(self, y: int) -> Strip:
        """Render a single line of the playlist."""
        return _render_line(self, y)

    def on_resize(self, event: Resize) -> None:
        """Handle terminal resize events."""
        self._adjust_scroll()
        self.refresh()

    def on_mount(self) -> None:
        """Handle mount event."""
        self._adjust_scroll()

    def _adjust_scroll(self) -> None:
        """Adjust scroll offset using Safe-Zone algorithm."""
        from platyplaty.ui.playlist_scroll import adjust_scroll

        adjust_scroll(self, self.size.height)

    def set_focused(self, focused: bool) -> None:
        """Set whether this widget is focused."""
        self._focused = focused
        self.refresh()

    def notify_playlist_changed(self) -> None:
        """Notify that the playlist contents have changed."""
        self._update_display_names()
        self._adjust_scroll()
        self.refresh()
