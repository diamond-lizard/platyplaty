"""Error view widget for displaying renderer error logs.

A full-screen overlay widget that displays renderer errors with
navigation and clear functionality.
"""

from textual.geometry import Size
from textual.strip import Strip
from textual.widget import Widget


class ErrorView(Widget):
    """Widget for displaying renderer error logs.

    Full-screen overlay with scrollable error list.
    """

    can_focus = True
    _error_log: list[str]
    _scroll_offset: int
    _wrapped_lines: list[str]

    def __init__(
        self,
        error_log: list[str],
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize the ErrorView widget."""
        super().__init__(name=name, id=id, classes=classes)
        self._error_log = error_log
        self._scroll_offset = 0
        self._wrapped_lines = []

    def get_content_width(self, container: Size, viewport: Size) -> int:
        """Return the content width."""
        return container.width

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        """Return the content height."""
        return container.height

    def _get_content_height(self) -> int:
        """Return the height available for content (excluding header/footer)."""
        return max(0, self.size.height - 2)

    def render_line(self, y: int) -> Strip:
        """Render a single line of the error view."""
        from platyplaty.ui.error_view_render import render_line

        return render_line(self, y, self.size.width)

    def on_mount(self) -> None:
        """Handle mount event."""
        self._update_wrapped_lines()

    def on_resize(self, event: object) -> None:
        """Handle terminal resize events."""
        self._update_wrapped_lines()
        self._clamp_scroll()
        self.refresh()

    def _update_wrapped_lines(self) -> None:
        """Update the wrapped lines cache for word wrapping."""
        from platyplaty.ui.error_view_wrap import wrap_error_lines

        self._wrapped_lines = wrap_error_lines(self._error_log, self.size.width)

    def _clamp_scroll(self) -> None:
        """Clamp scroll offset to valid range."""
        content_height = self._get_content_height()
        max_offset = max(0, len(self._wrapped_lines) - content_height)
        self._scroll_offset = max(0, min(self._scroll_offset, max_offset))

    def navigate_up(self) -> None:
        """Scroll up by one line."""
        if self._scroll_offset > 0:
            self._scroll_offset -= 1
            self.refresh()

    def navigate_down(self) -> None:
        """Scroll down by one line."""
        content_height = self._get_content_height()
        max_offset = max(0, len(self._wrapped_lines) - content_height)
        if self._scroll_offset < max_offset:
            self._scroll_offset += 1
            self.refresh()

    def notify_errors_changed(self) -> None:
        """Notify that the error log has changed."""
        self._update_wrapped_lines()
        self._clamp_scroll()
        self.refresh()
