#!/usr/bin/env python3
"""Unit tests for SHIFT-INSERT paste handling in command prompt."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.command_key import handle_command_key


@pytest.fixture
def mock_prompt():
    """Create a mock CommandPrompt with paste_from_selection."""
    prompt = MagicMock()
    prompt.input_text = ""
    prompt.cursor_index = 0
    prompt.paste_from_selection = MagicMock(return_value=True)
    return prompt


class TestShiftInsertPaste:
    """Tests for SHIFT-INSERT paste handling."""

    @pytest.mark.asyncio
    async def test_shift_insert_calls_paste_from_selection(self, mock_prompt):
        """SHIFT-INSERT calls paste_from_selection on the prompt."""
        await handle_command_key("shift+insert", mock_prompt, None)
        mock_prompt.paste_from_selection.assert_called_once()

    @pytest.mark.asyncio
    async def test_shift_insert_returns_true_on_success(self, mock_prompt):
        """SHIFT-INSERT returns True when paste_from_selection returns True."""
        mock_prompt.paste_from_selection.return_value = True
        result = await handle_command_key("shift+insert", mock_prompt, None)
        assert result is True

    @pytest.mark.asyncio
    async def test_shift_insert_returns_false_on_no_paste(self, mock_prompt):
        """SHIFT-INSERT returns False when paste_from_selection returns False."""
        mock_prompt.paste_from_selection.return_value = False
        result = await handle_command_key("shift+insert", mock_prompt, None)
        assert result is False
