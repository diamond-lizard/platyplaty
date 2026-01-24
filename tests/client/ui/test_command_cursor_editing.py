#!/usr/bin/env python3
"""Unit tests for cursor-aware text editing in command prompt."""

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


class TestCursorInsertion:
    """Tests for cursor-aware text insertion."""

    @pytest.mark.asyncio
    async def test_insert_at_middle(self, mock_prompt):
        """Character inserted at cursor position."""
        mock_prompt.input_text = "ac"
        mock_prompt.cursor_index = 1
        result = await handle_command_key("b", mock_prompt, "b")
        assert mock_prompt.input_text == "abc"
        assert mock_prompt.cursor_index == 2
        assert result is True

    @pytest.mark.asyncio
    async def test_insert_at_start(self, mock_prompt):
        """Character inserted at position 0."""
        mock_prompt.input_text = "bc"
        mock_prompt.cursor_index = 0
        result = await handle_command_key("a", mock_prompt, "a")
        assert mock_prompt.input_text == "abc"
        assert mock_prompt.cursor_index == 1
        assert result is True


class TestCursorBackspace:
    """Tests for cursor-aware backspace."""

    @pytest.mark.asyncio
    async def test_backspace_at_middle(self, mock_prompt):
        """Backspace deletes character before cursor."""
        mock_prompt.input_text = "abc"
        mock_prompt.cursor_index = 2
        result = await handle_command_key("backspace", mock_prompt, None)
        assert mock_prompt.input_text == "ac"
        assert mock_prompt.cursor_index == 1
        assert result is True

    @pytest.mark.asyncio
    async def test_backspace_at_start_is_noop(self, mock_prompt):
        """Backspace at position 0 is no-op."""
        mock_prompt.input_text = "abc"
        mock_prompt.cursor_index = 0
        result = await handle_command_key("backspace", mock_prompt, None)
        assert mock_prompt.input_text == "abc"
        assert mock_prompt.cursor_index == 0
        assert result is False


class TestDeleteKey:
    """Tests for delete key."""

    @pytest.mark.asyncio
    async def test_delete_at_middle(self, mock_prompt):
        """Delete removes character at cursor."""
        mock_prompt.input_text = "abc"
        mock_prompt.cursor_index = 1
        result = await handle_command_key("delete", mock_prompt, None)
        assert mock_prompt.input_text == "ac"
        assert mock_prompt.cursor_index == 1
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_at_end_is_noop(self, mock_prompt):
        """Delete at end of text is no-op."""
        mock_prompt.input_text = "abc"
        mock_prompt.cursor_index = 3
        result = await handle_command_key("delete", mock_prompt, None)
        assert mock_prompt.input_text == "abc"
        assert mock_prompt.cursor_index == 3
        assert result is False
