#!/usr/bin/env python3
"""Unit tests for command prompt key handling."""

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


class TestHandleCommandKeyCharacterInput:
    """Tests for character input handling."""

    @pytest.mark.asyncio
    async def test_space_character_adds_space(self, mock_prompt):
        """Space key adds a space character to input."""
        result = await handle_command_key("space", mock_prompt, " ")
        assert mock_prompt.input_text == " "
        assert mock_prompt.cursor_index == 1
        assert result is True

    @pytest.mark.asyncio
    async def test_letter_adds_letter(self, mock_prompt):
        """Letter key adds the letter to input."""
        result = await handle_command_key("a", mock_prompt, "a")
        assert mock_prompt.input_text == "a"
        assert mock_prompt.cursor_index == 1
        assert result is True

    @pytest.mark.asyncio
    async def test_multiple_characters(self, mock_prompt):
        """Multiple character inputs accumulate."""
        r1 = await handle_command_key("s", mock_prompt, "s")
        r2 = await handle_command_key("a", mock_prompt, "a")
        r3 = await handle_command_key("v", mock_prompt, "v")
        r4 = await handle_command_key("e", mock_prompt, "e")
        assert mock_prompt.input_text == "save"
        assert mock_prompt.cursor_index == 4
        assert all([r1, r2, r3, r4])

    @pytest.mark.asyncio
    async def test_none_character_does_not_add(self, mock_prompt):
        """Non-printable key with None character does not add text."""
        result = await handle_command_key("up", mock_prompt, None)
        assert mock_prompt.input_text == ""
        assert result is False


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
