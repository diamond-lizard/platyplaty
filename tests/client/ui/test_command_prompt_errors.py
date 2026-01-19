#!/usr/bin/env python3
"""Tests for command prompt error handling and input preservation."""

from platyplaty.ui.command_prompt import CommandPrompt


class TestCommandPromptInputPreservation:
    """Tests for input preservation behavior."""

    def test_initial_input_text_empty(self) -> None:
        """Input text starts empty."""
        prompt = CommandPrompt()
        assert prompt.input_text == ""

    def test_input_text_can_be_set(self) -> None:
        """Input text can be set directly."""
        prompt = CommandPrompt()
        prompt.input_text = "save "
        assert prompt.input_text == "save "

    def test_callback_can_be_set(self) -> None:
        """Callback can be set directly."""
        prompt = CommandPrompt()
        callback = lambda x: None
        prompt.callback = callback
        assert prompt.callback is callback

    def test_previous_focus_id_can_be_set(self) -> None:
        """Previous focus ID can be set directly."""
        prompt = CommandPrompt()
        prompt.previous_focus_id = "file-browser"
        assert prompt.previous_focus_id == "file-browser"

    def test_callback_initially_none(self) -> None:
        """Callback is initially None."""
        prompt = CommandPrompt()
        assert prompt.callback is None

    def test_previous_focus_id_initially_none(self) -> None:
        """Previous focus ID is initially None."""
        prompt = CommandPrompt()
        assert prompt.previous_focus_id is None
