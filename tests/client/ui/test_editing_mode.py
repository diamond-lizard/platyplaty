#!/usr/bin/env python3
"""Tests for editing mode Protocol and dataclasses.

This module tests the EditResult and PromptState dataclasses
defined in the editing_mode module.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.editing_mode import EditResult, PromptState


class TestPromptState:
    """Tests for PromptState dataclass."""

    def test_fields_are_accessible(self) -> None:
        """PromptState fields can be accessed."""
        state = PromptState(text="hello", cursor=3)
        assert state.text == "hello"
        assert state.cursor == 3

    def test_empty_text(self) -> None:
        """PromptState works with empty text."""
        state = PromptState(text="", cursor=0)
        assert state.text == ""
        assert state.cursor == 0


class TestEditResult:
    """Tests for EditResult dataclass."""

    def test_fields_are_accessible(self) -> None:
        """EditResult fields can be accessed."""
        result = EditResult(new_text="world", new_cursor=5, state_changed=True)
        assert result.new_text == "world"
        assert result.new_cursor == 5
        assert result.state_changed is True

    def test_state_changed_false(self) -> None:
        """EditResult can indicate no state change."""
        result = EditResult(new_text="same", new_cursor=0, state_changed=False)
        assert result.state_changed is False
