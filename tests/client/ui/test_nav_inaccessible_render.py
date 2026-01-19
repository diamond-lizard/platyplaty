#!/usr/bin/env python3
"""Tests for rendering of inaccessible directory message.

This module tests that FileBrowser correctly renders the
'inaccessible directory' message when permission_denied=True.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.directory_types import DirectoryListing
from platyplaty.ui.file_browser_pane_render import render_pane_line


class TestInaccessibleDirectoryRendering:
    """Tests for rendering of inaccessible directory message."""

    def test_renders_inaccessible_directory_message(self) -> None:
        """FileBrowser renders 'inaccessible directory' when permission_denied=True."""
        # Create a listing with permission_denied=True
        listing = DirectoryListing(
            entries=[],
            was_empty=False,
            had_filtered_entries=False,
            permission_denied=True,
        )

        # Render line 0 (the message line)
        result = render_pane_line(listing, y=0, width=30, is_left_pane=False)

        # Result is now list[Segment], check first segment text
        assert len(result) == 1, "should have one segment"
        segment_text = result[0].text
        assert "inaccessible directory" in segment_text, "should contain message"
        assert len(segment_text) == 30, "should be padded to width"
