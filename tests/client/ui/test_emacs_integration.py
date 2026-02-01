#!/usr/bin/env python3
"""Integration tests for emacs editing mode through handle_command_key.

These tests verify that emacs keybindings work correctly when invoked
through the full handle_command_key path, using FakePrompt and real
EmacsEditingMode.
"""

import pytest

from platyplaty.ui.command_key import handle_command_key
from platyplaty.ui.emacs_editing import EmacsEditingMode
from platyplaty.ui.editing_mode import PromptState


class TestEmacsKeysViaHandleCommandKey:
    """Tests for emacs keys through handle_command_key."""

    @pytest.mark.asyncio
    async def test_ctrl_a_through_full_path(self, test_prompt) -> None:
        """Ctrl+A moves cursor to start through handle_command_key."""
        mode = EmacsEditingMode()
        test_prompt.input_text = "hello world"
        test_prompt.cursor_index = 6

        result = await handle_command_key("ctrl+a", test_prompt, None, mode)

        assert result is True
        assert test_prompt.cursor_index == 0
        assert test_prompt.input_text == "hello world"

    @pytest.mark.asyncio
    async def test_ctrl_y_yank_through_full_path(self, test_prompt) -> None:
        """Ctrl+Y yanks from buffer through handle_command_key."""
        mode = EmacsEditingMode()
        mode._yank_buffer = "yanked"
        test_prompt.input_text = "hello"
        test_prompt.cursor_index = 5

        result = await handle_command_key("ctrl+y", test_prompt, None, mode)

        assert result is True
        assert test_prompt.input_text == "helloyanked"
        assert test_prompt.cursor_index == 11


class TestExistingKeysStillWork:
    """Tests that existing basic keys work with emacs mode active."""

    @pytest.mark.asyncio
    async def test_left_arrow_still_works(self, test_prompt) -> None:
        """Left arrow moves cursor back one character."""
        mode = EmacsEditingMode()
        test_prompt.input_text = "hello"
        test_prompt.cursor_index = 3

        result = await handle_command_key("left", test_prompt, None, mode)

        assert result is True
        assert test_prompt.cursor_index == 2

    @pytest.mark.asyncio
    async def test_right_arrow_still_works(self, test_prompt) -> None:
        """Right arrow moves cursor forward one character."""
        mode = EmacsEditingMode()
        test_prompt.input_text = "hello"
        test_prompt.cursor_index = 2

        result = await handle_command_key("right", test_prompt, None, mode)

        assert result is True
        assert test_prompt.cursor_index == 3

    @pytest.mark.asyncio
    async def test_backspace_still_works(self, test_prompt) -> None:
        """Backspace deletes character before cursor."""
        mode = EmacsEditingMode()
        test_prompt.input_text = "hello"
        test_prompt.cursor_index = 3

        result = await handle_command_key("backspace", test_prompt, None, mode)

        assert result is True
        assert test_prompt.input_text == "helo"
        assert test_prompt.cursor_index == 2

    @pytest.mark.asyncio
    async def test_character_insertion_still_works(self, test_prompt) -> None:
        """Character insertion works with emacs mode active."""
        mode = EmacsEditingMode()
        test_prompt.input_text = "hllo"
        test_prompt.cursor_index = 1

        result = await handle_command_key("e", test_prompt, "e", mode)

        assert result is True
        assert test_prompt.input_text == "hello"
        assert test_prompt.cursor_index == 2
