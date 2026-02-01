#!/usr/bin/env python3
"""Tests for editing mode wiring into application.

These tests verify that the editing mode is properly wired into
AppContext and CommandPrompt, and that handle_command_key correctly
delegates to the editing mode.
"""

import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.emacs_editing import EmacsEditingMode


class TestAppContextEditingMode:
    """Tests for editing_mode in AppContext."""

    def test_editing_mode_accessible_from_context(self, minimal_app_context):
        """editing_mode is accessible from AppContext."""
        assert hasattr(minimal_app_context, "editing_mode")
        assert minimal_app_context.editing_mode is not None

    def test_editing_mode_is_emacs_by_default(self, minimal_app_context):
        """Default editing_mode is EmacsEditingMode."""
        assert isinstance(minimal_app_context.editing_mode, EmacsEditingMode)


class TestHandleCommandKeyDelegation:
    """Tests that handle_command_key delegates to editing_mode.handle_key."""

    @pytest.mark.asyncio
    async def test_ctrl_a_delegated_to_editing_mode(
        self, test_prompt, null_editing_mode
    ) -> None:
        """Ctrl+A is delegated to editing mode and moves cursor."""
        from platyplaty.ui.command_key import handle_command_key
        from platyplaty.ui.emacs_editing import EmacsEditingMode

        # Use real EmacsEditingMode instead of null
        mode = EmacsEditingMode()
        test_prompt.input_text = "hello"
        test_prompt.cursor_index = 3

        result = await handle_command_key("ctrl+a", test_prompt, None, mode)

        assert result is True
        assert test_prompt.cursor_index == 0

    @pytest.mark.asyncio
    async def test_ctrl_e_delegated_to_editing_mode(
        self, test_prompt, null_editing_mode
    ) -> None:
        """Ctrl+E is delegated to editing mode and moves cursor to end."""
        from platyplaty.ui.command_key import handle_command_key
        from platyplaty.ui.emacs_editing import EmacsEditingMode

        mode = EmacsEditingMode()
        test_prompt.input_text = "hello"
        test_prompt.cursor_index = 0

        result = await handle_command_key("ctrl+e", test_prompt, None, mode)

        assert result is True
        assert test_prompt.cursor_index == 5
