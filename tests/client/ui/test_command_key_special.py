#!/usr/bin/env python3
"""Unit tests for special key handling in command prompt."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.command_key import handle_command_key



class TestHandleCommandKeySpecialKeys:
    """Tests for special key handling."""

    @pytest.mark.asyncio
    async def test_escape_hides_prompt(self, test_prompt):
        """Escape key hides the prompt."""
        result = await handle_command_key("escape", test_prompt, None)
        assert test_prompt.hidden is True
        assert result is False


    @pytest.mark.asyncio
    async def test_ctrl_c_hides_prompt(self, test_prompt):
        """Ctrl+C hides the prompt like Escape."""
        result = await handle_command_key("ctrl+c", test_prompt, None)
        assert test_prompt.hidden is True
        assert result is False

    @pytest.mark.asyncio
    async def test_backspace_removes_character(self, test_prompt):
        """Backspace removes the last character."""
        test_prompt.input_text = "save"
        test_prompt.cursor_index = 4
        result = await handle_command_key("backspace", test_prompt, None)
        assert test_prompt.input_text == "sav"
        assert test_prompt.cursor_index == 3
        assert result is True

    @pytest.mark.asyncio
    async def test_backspace_on_empty_is_safe(self, test_prompt):
        """Backspace on empty input does not error."""
        test_prompt.input_text = ""
        result = await handle_command_key("backspace", test_prompt, None)
        assert test_prompt.input_text == ""
        assert result is False

    @pytest.mark.asyncio
    async def test_enter_with_text_calls_callback(self, test_prompt):
        """Enter with text and callback calls the callback."""
        test_prompt.input_text = "clear"
        called_with = []
        async def track_callback(text: str) -> None:
            called_with.append(text)
        test_prompt.callback = track_callback
        result = await handle_command_key("enter", test_prompt, None)
        assert called_with == ["clear"]
        assert result is False

    @pytest.mark.asyncio
    async def test_enter_without_text_hides_prompt(self, test_prompt):
        """Enter with empty input hides the prompt."""
        test_prompt.input_text = ""
        result = await handle_command_key("enter", test_prompt, None)
        assert test_prompt.hidden is True
        assert result is False

    @pytest.mark.asyncio
    async def test_enter_without_callback_hides_prompt(self, test_prompt):
        """Enter without callback hides the prompt."""
        test_prompt.input_text = "clear"
        test_prompt.callback = None
        result = await handle_command_key("enter", test_prompt, None)
        assert test_prompt.hidden is True
        assert result is False
