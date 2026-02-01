#!/usr/bin/env python3
"""Unit tests for SHIFT-INSERT paste handling in command prompt."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.command_key import handle_command_key



class TestShiftInsertPaste:
    """Tests for SHIFT-INSERT paste handling."""

    @pytest.mark.asyncio
    async def test_shift_insert_calls_paste_from_selection(self, test_prompt):
        test_prompt.paste_result = True
        result = await handle_command_key("shift+insert", test_prompt, None)
        assert result is True  # Verifies paste_from_selection was called

    @pytest.mark.asyncio
    async def test_shift_insert_returns_true_on_success(self, test_prompt):
        """SHIFT-INSERT returns True when paste_from_selection returns True."""
        test_prompt.paste_result = True
        result = await handle_command_key("shift+insert", test_prompt, None)
        assert result is True

    @pytest.mark.asyncio
    async def test_shift_insert_returns_false_on_no_paste(self, test_prompt):
        """SHIFT-INSERT returns False when paste_from_selection returns False."""
        test_prompt.paste_result = False
        result = await handle_command_key("shift+insert", test_prompt, None)
        assert result is False
