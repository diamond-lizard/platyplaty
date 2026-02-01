#!/usr/bin/env python3
"""Unit tests for command prompt key handling."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.command_key import handle_command_key



class TestHandleCommandKeyCharacterInput:
    """Tests for character input handling."""

    @pytest.mark.asyncio
    async def test_space_character_adds_space(self, test_prompt):
        """Space key adds a space character to input."""
        result = await handle_command_key("space", test_prompt, " ")
        assert test_prompt.input_text == " "
        assert test_prompt.cursor_index == 1
        assert result is True

    @pytest.mark.asyncio
    async def test_letter_adds_letter(self, test_prompt):
        """Letter key adds the letter to input."""
        result = await handle_command_key("a", test_prompt, "a")
        assert test_prompt.input_text == "a"
        assert test_prompt.cursor_index == 1
        assert result is True

    @pytest.mark.asyncio
    async def test_multiple_characters(self, test_prompt):
        """Multiple character inputs accumulate."""
        r1 = await handle_command_key("s", test_prompt, "s")
        r2 = await handle_command_key("a", test_prompt, "a")
        r3 = await handle_command_key("v", test_prompt, "v")
        r4 = await handle_command_key("e", test_prompt, "e")
        assert test_prompt.input_text == "save"
        assert test_prompt.cursor_index == 4
        assert all([r1, r2, r3, r4])

    @pytest.mark.asyncio
    async def test_none_character_does_not_add(self, test_prompt):
        """Non-printable key with None character does not add text."""
        result = await handle_command_key("up", test_prompt, None)
        assert test_prompt.input_text == ""
        assert result is False

    @pytest.mark.asyncio
    async def test_control_character_not_inserted(self, test_prompt):
        """Control characters are rejected, not inserted."""
        result = await handle_command_key("ctrl+k", test_prompt, "\x0b")
        assert test_prompt.input_text == ""
        assert result is False

