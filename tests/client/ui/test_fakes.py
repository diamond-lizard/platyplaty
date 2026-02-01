#!/usr/bin/env python3
"""Fake implementations for testing.

This module provides Fake test doubles that implement project Protocols,
following the "Don't Mock What You Don't Own" principle. These Fakes
provide predictable behavior without mock configuration.
"""


class FakePrompt:
    """Fake implementation of PromptInterface for testing.

    This provides predictable behavior without mock configuration,
    following the "Don't Mock What You Don't Own" principle.
    """

    def __init__(self) -> None:
        """Initialize with empty input and cursor at position 0."""
        self.input_text: str = ""
        self.cursor_index: int = 0
        self.callback = None
        self.hidden: bool = False
        self.paste_result: bool = False

    def update_cursor_with_scroll(self, new_cursor: int) -> None:
        """Update cursor position."""
        self.cursor_index = new_cursor

    def hide(self) -> None:
        """Mark the prompt as hidden."""
        self.hidden = True

    def paste_from_selection(self) -> bool:
        """Return the configured paste result."""
        return self.paste_result


def create_mock_browser():
    """Create a mock FileBrowser for testing.

    The mock is configured so that set_selection_by_index(idx) updates
    browser.selected_index. This mirrors real FileBrowser behavior.
    """
    from unittest.mock import MagicMock
    browser = MagicMock()
    browser.app = MagicMock()
    browser.app.ctx = MagicMock()
    browser.app.ctx.playlist = MagicMock()
    browser.app.ctx.autoplay_manager = MagicMock()
    browser._adjust_scroll = MagicMock()
    browser.refresh = MagicMock()
    browser.set_selection_by_index = MagicMock(
        side_effect=lambda idx: setattr(browser, 'selected_index', idx)
    )
    return browser


def make_listing(entries: list):
    """Create a DirectoryListing from a list of entries."""
    from platyplaty.ui.directory_types import DirectoryListing
    return DirectoryListing(
        entries=entries,
        was_empty=False,
        had_filtered_entries=False,
        permission_denied=False,
    )
