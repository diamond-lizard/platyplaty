#!/usr/bin/env python3
"""Unit tests for command prompt cursor navigation and editing."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.command_key import handle_command_key



class TestCursorNavigation:
    """Tests for cursor navigation keys."""

    @pytest.mark.asyncio
    async def test_left_decrements_cursor(self, test_prompt):
        """Left arrow decrements cursor index."""
        test_prompt.input_text = "abc"
        test_prompt.cursor_index = 2
        result = await handle_command_key("left", test_prompt, None)
        assert test_prompt.cursor_index == 1
        assert result is True

    @pytest.mark.asyncio
    async def test_left_clamps_at_zero(self, test_prompt):
        """Left arrow at position 0 is no-op."""
        test_prompt.input_text = "abc"
        test_prompt.cursor_index = 0
        result = await handle_command_key("left", test_prompt, None)
        assert test_prompt.cursor_index == 0
        assert result is False

    @pytest.mark.asyncio
    async def test_right_increments_cursor(self, test_prompt):
        """Right arrow increments cursor index."""
        test_prompt.input_text = "abc"
        test_prompt.cursor_index = 1
        result = await handle_command_key("right", test_prompt, None)
        assert test_prompt.cursor_index == 2
        assert result is True

    @pytest.mark.asyncio
    async def test_right_clamps_at_length(self, test_prompt):
        """Right arrow at end of text is no-op."""
        test_prompt.input_text = "abc"
        test_prompt.cursor_index = 3
        result = await handle_command_key("right", test_prompt, None)
        assert test_prompt.cursor_index == 3
        assert result is False

    @pytest.mark.asyncio
    async def test_home_moves_to_start(self, test_prompt):
        """Home key moves cursor to position 0."""
        test_prompt.input_text = "abc"
        test_prompt.cursor_index = 2
        result = await handle_command_key("home", test_prompt, None)
        assert test_prompt.cursor_index == 0
        assert result is True

    @pytest.mark.asyncio
    async def test_home_at_start_is_noop(self, test_prompt):
        """Home at position 0 is no-op."""
        test_prompt.input_text = "abc"
        test_prompt.cursor_index = 0
        result = await handle_command_key("home", test_prompt, None)
        assert test_prompt.cursor_index == 0
        assert result is False

    @pytest.mark.asyncio
    async def test_end_moves_to_end(self, test_prompt):
        """End key moves cursor to end of text."""
        test_prompt.input_text = "abc"
        test_prompt.cursor_index = 1
        result = await handle_command_key("end", test_prompt, None)
        assert test_prompt.cursor_index == 3
        assert result is True

    @pytest.mark.asyncio
    async def test_end_at_end_is_noop(self, test_prompt):
        """End at end of text is no-op."""
        test_prompt.input_text = "abc"
        test_prompt.cursor_index = 3
        result = await handle_command_key("end", test_prompt, None)
        assert test_prompt.cursor_index == 3
        assert result is False
