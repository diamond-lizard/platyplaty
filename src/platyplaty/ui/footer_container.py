#!/usr/bin/env python3
"""Footer container widget for status line and command line.

This module provides a container widget that hosts StatusLine and CommandLine
as children. The footer docks to the bottom of the terminal with height 2.
"""

from textual.app import ComposeResult
from textual.widget import Widget

from platyplaty.ui.command_line import CommandLine
from platyplaty.ui.status_line import StatusLine


class FooterContainer(Widget):
    """Container for the bottom two rows: StatusLine and CommandLine.

    StatusLine appears on top (first row), CommandLine on bottom (second row).
    """

    DEFAULT_CSS = """
    FooterContainer {
        dock: bottom;
        height: 2;
    }
    """

    def __init__(
        self,
        error_log: list[str],
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize the FooterContainer widget.

        Args:
            error_log: Shared error log list for StatusLine.
            name: Optional widget name.
            id: Optional widget ID.
            classes: Optional CSS classes.
        """
        super().__init__(name=name, id=id, classes=classes)
        self._error_log = error_log

    def compose(self) -> ComposeResult:
        """Yield StatusLine and CommandLine as children."""
        yield StatusLine(self._error_log, id="status_line")
        yield CommandLine(id="command_line")
