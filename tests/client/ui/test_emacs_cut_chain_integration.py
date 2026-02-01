#!/usr/bin/env python3
"""Integration tests for emacs cut chain breaking behavior.

These tests verify that non-emacs keys properly break the consecutive
cut chain when invoked through handle_command_key.
"""

import pytest

from platyplaty.ui.command_key import handle_command_key
from platyplaty.ui.emacs_editing import EmacsEditingMode


class TestNonEmacsKeysBreakCutChain:
    """Tests that non-emacs keys break the consecutive cut chain."""

    @pytest.mark.asyncio
    async def test_shift_insert_breaks_cut_chain(self, test_prompt) -> None:
        """Shift+Insert breaks cut chain; second cut replaces buffer."""
        mode = EmacsEditingMode()

        # First cut with Ctrl+K
        test_prompt.input_text = "hello world"
        test_prompt.cursor_index = 6
        await handle_command_key("ctrl+k", test_prompt, None, mode)
        assert mode.yank_buffer == "world"
        assert mode._last_was_cut is True

        # Shift+Insert (paste from X11) - breaks chain
        await handle_command_key("shift+insert", test_prompt, None, mode)
        assert mode._last_was_cut is False

        # Second cut with Ctrl+K - should replace, not append
        test_prompt.input_text = "hello test"
        test_prompt.cursor_index = 6
        await handle_command_key("ctrl+k", test_prompt, None, mode)

        assert mode.yank_buffer == "test"  # Replaced, not "worldtest"

    @pytest.mark.asyncio
    async def test_arrow_keys_break_cut_chain(self, test_prompt) -> None:
        """Arrow keys break cut chain; second cut replaces buffer."""
        mode = EmacsEditingMode()

        # First cut with Ctrl+K
        test_prompt.input_text = "ab"
        test_prompt.cursor_index = 1
        await handle_command_key("ctrl+k", test_prompt, None, mode)
        assert mode.yank_buffer == "b"
        assert mode._last_was_cut is True

        # Left arrow - breaks chain
        await handle_command_key("left", test_prompt, None, mode)
        assert mode._last_was_cut is False

        # Second cut - should replace, not append
        test_prompt.input_text = "cd"
        test_prompt.cursor_index = 1
        await handle_command_key("ctrl+k", test_prompt, None, mode)

        assert mode.yank_buffer == "d"  # Replaced, not "bd"

    @pytest.mark.asyncio
    async def test_character_insertion_breaks_cut_chain(
        self, test_prompt
    ) -> None:
        """Character insertion breaks cut chain."""
        mode = EmacsEditingMode()

        # First cut with Ctrl+K
        test_prompt.input_text = "ab"
        test_prompt.cursor_index = 1
        await handle_command_key("ctrl+k", test_prompt, None, mode)
        assert mode.yank_buffer == "b"

        # Character insertion - breaks chain
        await handle_command_key("x", test_prompt, "x", mode)
        assert mode._last_was_cut is False

        # Second cut - should replace, not append
        test_prompt.input_text = "yz"
        test_prompt.cursor_index = 1
        await handle_command_key("ctrl+k", test_prompt, None, mode)

        assert mode.yank_buffer == "z"  # Replaced, not "bz"
