#!/usr/bin/env python3
"""Unit tests for cursor-aware text editing in command prompt."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.command_key import handle_command_key



class TestCursorInsertion:
    """Tests for cursor-aware text insertion."""

    @pytest.mark.asyncio
    async def test_insert_at_middle(self, test_prompt):
        """Character inserted at cursor position."""
        test_prompt.input_text = "ac"
        test_prompt.cursor_index = 1
        result = await handle_command_key("b", test_prompt, "b")
        assert test_prompt.input_text == "abc"
        assert test_prompt.cursor_index == 2
        assert result is True

    @pytest.mark.asyncio
    async def test_insert_at_start(self, test_prompt):
        """Character inserted at position 0."""
        test_prompt.input_text = "bc"
        test_prompt.cursor_index = 0
        result = await handle_command_key("a", test_prompt, "a")
        assert test_prompt.input_text == "abc"
        assert test_prompt.cursor_index == 1
        assert result is True


class TestCursorBackspace:
    """Tests for cursor-aware backspace."""

    @pytest.mark.asyncio
    async def test_backspace_at_middle(self, test_prompt):
        """Backspace deletes character before cursor."""
        test_prompt.input_text = "abc"
        test_prompt.cursor_index = 2
        result = await handle_command_key("backspace", test_prompt, None)
        assert test_prompt.input_text == "ac"
        assert test_prompt.cursor_index == 1
        assert result is True

    @pytest.mark.asyncio
    async def test_backspace_at_start_is_noop(self, test_prompt):
        """Backspace at position 0 is no-op."""
        test_prompt.input_text = "abc"
        test_prompt.cursor_index = 0
        result = await handle_command_key("backspace", test_prompt, None)
        assert test_prompt.input_text == "abc"
        assert test_prompt.cursor_index == 0
        assert result is False


class TestDeleteKey:
    """Tests for delete key."""

    @pytest.mark.asyncio
    async def test_delete_at_middle(self, test_prompt):
        """Delete removes character at cursor."""
        test_prompt.input_text = "abc"
        test_prompt.cursor_index = 1
        result = await handle_command_key("delete", test_prompt, None)
        assert test_prompt.input_text == "ac"
        assert test_prompt.cursor_index == 1
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_at_end_is_noop(self, test_prompt):
        """Delete at end of text is no-op."""
        test_prompt.input_text = "abc"
        test_prompt.cursor_index = 3
        result = await handle_command_key("delete", test_prompt, None)
        assert test_prompt.input_text == "abc"
        assert test_prompt.cursor_index == 3
        assert result is False
