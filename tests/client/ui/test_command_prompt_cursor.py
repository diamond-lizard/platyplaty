#!/usr/bin/env python3
"""Unit tests for command prompt cursor navigation and editing."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.command_key import handle_command_key


@pytest.fixture
def mock_prompt():
    """Create a mock CommandPrompt with cursor support."""
    prompt = MagicMock()
    prompt.input_text = ""
    prompt.cursor_index = 0
    prompt.callback = None
    prompt.hide = MagicMock()
    return prompt


class TestCursorNavigation:
    """Tests for cursor navigation keys."""

    @pytest.mark.asyncio
    async def test_left_decrements_cursor(self, mock_prompt):
        """Left arrow decrements cursor index."""
        mock_prompt.input_text = "abc"
        mock_prompt.cursor_index = 2
        result = await handle_command_key("left", mock_prompt, None)
        assert mock_prompt.cursor_index == 1
        assert result is True

    @pytest.mark.asyncio
    async def test_left_clamps_at_zero(self, mock_prompt):
        """Left arrow at position 0 is no-op."""
        mock_prompt.input_text = "abc"
        mock_prompt.cursor_index = 0
        result = await handle_command_key("left", mock_prompt, None)
        assert mock_prompt.cursor_index == 0
        assert result is False

    @pytest.mark.asyncio
    async def test_right_increments_cursor(self, mock_prompt):
        """Right arrow increments cursor index."""
        mock_prompt.input_text = "abc"
        mock_prompt.cursor_index = 1
        result = await handle_command_key("right", mock_prompt, None)
        assert mock_prompt.cursor_index == 2
        assert result is True

    @pytest.mark.asyncio
    async def test_right_clamps_at_length(self, mock_prompt):
        """Right arrow at end of text is no-op."""
        mock_prompt.input_text = "abc"
        mock_prompt.cursor_index = 3
        result = await handle_command_key("right", mock_prompt, None)
        assert mock_prompt.cursor_index == 3
        assert result is False

    @pytest.mark.asyncio
    async def test_home_moves_to_start(self, mock_prompt):
        """Home key moves cursor to position 0."""
        mock_prompt.input_text = "abc"
        mock_prompt.cursor_index = 2
        result = await handle_command_key("home", mock_prompt, None)
        assert mock_prompt.cursor_index == 0
        assert result is True

    @pytest.mark.asyncio
    async def test_home_at_start_is_noop(self, mock_prompt):
        """Home at position 0 is no-op."""
        mock_prompt.input_text = "abc"
        mock_prompt.cursor_index = 0
        result = await handle_command_key("home", mock_prompt, None)
        assert mock_prompt.cursor_index == 0
        assert result is False

    @pytest.mark.asyncio
    async def test_end_moves_to_end(self, mock_prompt):
        """End key moves cursor to end of text."""
        mock_prompt.input_text = "abc"
        mock_prompt.cursor_index = 1
        result = await handle_command_key("end", mock_prompt, None)
        assert mock_prompt.cursor_index == 3
        assert result is True

    @pytest.mark.asyncio
    async def test_end_at_end_is_noop(self, mock_prompt):
        """End at end of text is no-op."""
        mock_prompt.input_text = "abc"
        mock_prompt.cursor_index = 3
        result = await handle_command_key("end", mock_prompt, None)
        assert mock_prompt.cursor_index == 3
        assert result is False
