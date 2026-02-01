#!/usr/bin/env python3
"""Integration tests for emacs editing mode state persistence.

These tests verify that the editing mode state (yank buffer) persists
correctly across prompt invocations through handle_command_key.
"""

import pytest

from platyplaty.ui.command_key import handle_command_key
from platyplaty.ui.emacs_editing import EmacsEditingMode


class TestEditingModeStatePersistence:
    """Tests that editing mode state persists across prompt invocations."""

    @pytest.mark.asyncio
    async def test_yank_buffer_persists_across_prompt_sessions(
        self, test_prompt
    ) -> None:
        """Yank buffer persists while cut chain is reset on prompt reopen."""
        mode = EmacsEditingMode()

        # Session 1: Cut some text with Ctrl+K
        test_prompt.input_text = "hello world"
        test_prompt.cursor_index = 6
        await handle_command_key("ctrl+k", test_prompt, None, mode)
        assert test_prompt.input_text == "hello "
        assert mode.yank_buffer == "world"

        # Simulate prompt close and reopen (reset_transient_state)
        mode.reset_transient_state()

        # Session 2: Yank with Ctrl+Y - buffer should still have "world"
        test_prompt.input_text = "new "
        test_prompt.cursor_index = 4
        await handle_command_key("ctrl+y", test_prompt, None, mode)

        assert test_prompt.input_text == "new world"
        assert test_prompt.cursor_index == 9
