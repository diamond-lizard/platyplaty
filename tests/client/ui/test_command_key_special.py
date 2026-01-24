#!/usr/bin/env python3
"""Unit tests for special key handling in command prompt."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.command_key import handle_command_key


@pytest.fixture
def mock_prompt():
    """Create a mock CommandPrompt."""
    prompt = MagicMock()
    prompt.input_text = ""
    prompt.callback = None
    prompt.cursor_index = 0
    prompt.hide = MagicMock()
    return prompt


class TestHandleCommandKeySpecialKeys:
    """Tests for special key handling."""

    @pytest.mark.asyncio
    async def test_escape_hides_prompt(self, mock_prompt):
        """Escape key hides the prompt."""
        result = await handle_command_key("escape", mock_prompt, None)
        mock_prompt.hide.assert_called_once()
        assert result is False

    @pytest.mark.asyncio
    async def test_backspace_removes_character(self, mock_prompt):
        """Backspace removes the last character."""
        mock_prompt.input_text = "save"
        mock_prompt.cursor_index = 4
        result = await handle_command_key("backspace", mock_prompt, None)
        assert mock_prompt.input_text == "sav"
        assert mock_prompt.cursor_index == 3
        assert result is True

    @pytest.mark.asyncio
    async def test_backspace_on_empty_is_safe(self, mock_prompt):
        """Backspace on empty input does not error."""
        mock_prompt.input_text = ""
        result = await handle_command_key("backspace", mock_prompt, None)
        assert mock_prompt.input_text == ""
        assert result is False

    @pytest.mark.asyncio
    async def test_enter_with_text_calls_callback(self, mock_prompt):
        """Enter with text and callback calls the callback."""
        mock_prompt.input_text = "clear"
        mock_prompt.callback = AsyncMock()
        result = await handle_command_key("enter", mock_prompt, None)
        mock_prompt.callback.assert_called_once_with("clear")
        assert result is False

    @pytest.mark.asyncio
    async def test_enter_without_text_hides_prompt(self, mock_prompt):
        """Enter with empty input hides the prompt."""
        mock_prompt.input_text = ""
        result = await handle_command_key("enter", mock_prompt, None)
        mock_prompt.hide.assert_called_once()
        assert result is False

    @pytest.mark.asyncio
    async def test_enter_without_callback_hides_prompt(self, mock_prompt):
        """Enter without callback hides the prompt."""
        mock_prompt.input_text = "clear"
        mock_prompt.callback = None
        result = await handle_command_key("enter", mock_prompt, None)
        mock_prompt.hide.assert_called_once()
        assert result is False
