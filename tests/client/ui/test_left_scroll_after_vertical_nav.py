#!/usr/bin/env python3
"""Tests for left pane scroll preservation after vertical navigation.

This module tests that after up/down navigation in the middle pane,
the left pane scroll offset is adjusted to keep the current directory
visible.

Regression test for bug: left pane scroll resets to 0 after up/down
navigation, making the current directory invisible when it was far
down in the parent directory listing.
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from left_scroll_test_helpers import (
    is_index_visible,
    make_large_left_listing,
    make_mock_browser,
    make_small_middle_listing,
    setup_nav_state_mock,
)


class TestLeftScrollAfterVerticalNav:
    """Tests for left pane scroll preservation after up/down navigation."""

    def test_left_scroll_preserved_after_sync_from_nav_state(self) -> None:
        """Left pane scroll should keep current directory visible after sync.

        This tests the bug where sync_from_nav_state() resets
        _left_scroll_offset to 0 (from parent memory), making the
        current directory invisible when it was far down in the list.

        The fix should call adjust_left_pane_scroll() after
        sync_from_nav_state() in up/down navigation.
        """
        from platyplaty.ui.file_browser_scroll import adjust_left_pane_scroll

        left_listing, current_dir_name, current_dir_index = make_large_left_listing(current_dir_name="platyplaty")

        middle_listing = make_small_middle_listing()

        # Create browser where current dir is far down in parent (index 129)
        # but scroll is set correctly to make it visible (e.g., 106)
        browser = make_mock_browser(
            left_listing=left_listing,
            middle_listing=middle_listing,
            current_dir_name=current_dir_name,
            left_scroll_offset=106,  # Correct scroll to see index 129
            selected_index=0,
        )

        # First verify adjust_left_pane_scroll works correctly
        pane_height = 31
        adjust_left_pane_scroll(browser, pane_height)
        correct_scroll = browser._left_scroll_offset

        # Now simulate what sync_from_nav_state does: reset to 0
        # (simulating get_parent_scroll_offset returning 0)
        browser._left_scroll_offset = 0

        # The bug: after reset, current dir should NOT be visible
        assert not is_index_visible(browser._left_scroll_offset, pane_height, current_dir_index), \
            "Bug precondition: index should NOT be visible with scroll=0"

        # The fix: call adjust_left_pane_scroll after sync
        adjust_left_pane_scroll(browser, pane_height)

        # Now verify current directory is visible
        assert is_index_visible(browser._left_scroll_offset, pane_height, current_dir_index), \
            "After fix: current dir should be visible"

    @pytest.mark.asyncio
    async def test_action_nav_down_preserves_left_scroll(self) -> None:
        """action_nav_down should preserve left pane scroll visibility.

        This is a regression test: after pressing down in the middle pane,
        the current directory should remain visible in the left pane.
        The bug was that sync_from_nav_state reset _left_scroll_offset
        to 0 without re-adjusting it.
        """
        from platyplaty.ui.file_browser_nav_updown import action_nav_down
        from platyplaty.ui.file_browser_scroll import adjust_left_pane_scroll

        left_listing, current_dir_name, current_dir_index = make_large_left_listing()

        middle_listing = make_small_middle_listing()

        # Create mock browser
        browser = make_mock_browser(
            left_listing=left_listing,
            middle_listing=middle_listing,
            current_dir_name=current_dir_name,
            left_scroll_offset=106,  # Correct scroll to see index 129
            selected_index=0,  # At first item in middle pane
        )

        setup_nav_state_mock(browser, middle_listing, parent_scroll=0)

        pane_height = 31

        # Verify precondition: current dir is visible before nav
        adjust_left_pane_scroll(browser, pane_height)
        assert is_index_visible(browser._left_scroll_offset, pane_height, current_dir_index), \
            "Precondition: current dir should be visible initially"

        # Patch get_right_pane_content to avoid mock path issues
        with patch(
            "platyplaty.ui.file_browser_refresh.get_right_pane_content",
            return_value=None,
        ):
            await action_nav_down(browser)

        # After navigation, current dir should STILL be visible
        assert is_index_visible(browser._left_scroll_offset, pane_height, current_dir_index), \
            "After nav_down: current dir should be visible"
