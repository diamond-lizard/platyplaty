#!/usr/bin/env python3
"""Command line widget container for prompts and transient errors.

This module provides a container widget that hosts CommandPrompt,
TransientErrorBar, and ConfirmationPrompt as children. The Command Line
appears at the very bottom of the terminal, with the Status Line above it.
"""

from collections.abc import Awaitable, Callable

from textual.app import ComposeResult
from textual.widget import Widget

from platyplaty.ui.command_prompt import CommandPrompt
from platyplaty.ui.confirmation_prompt import ConfirmationPrompt
from platyplaty.ui.persistent_message import PersistentMessage
from platyplaty.ui.transient_error import TransientErrorBar


class CommandLine(Widget):
    """A container for command prompt, confirmation prompt, and errors.

    The Command Line is blank by default (black background, white foreground).
    It shows one of its child widgets when activated:
    - CommandPrompt for : commands
    - ConfirmationPrompt for y/n prompts
    - TransientErrorBar for brief error messages
    """

    DEFAULT_CSS = """
    CommandLine {
        height: 1;
        background: black;
        color: white;
    }
    """

    def compose(self) -> ComposeResult:
        """Yield child widgets: CommandPrompt, TransientErrorBar, ConfirmationPrompt."""
        yield CommandPrompt(id="command_prompt")
        yield TransientErrorBar(id="transient_error")
        yield ConfirmationPrompt(id="confirmation_prompt")
        yield PersistentMessage(id="persistent_message")

    def show_command_prompt(
        self,
        callback: Callable[[str], Awaitable[None]],
        previous_focus_id: str | None = None,
        initial_text: str = "",
    ) -> None:
        """Display the command prompt.

        Args:
            callback: Function to call with entered text.
            previous_focus_id: Widget ID to return focus to on dismiss.
            initial_text: Initial text to populate the prompt with.
        """
        error_bar = self.query_one("#transient_error", TransientErrorBar)
        if error_bar.has_class("visible"):
            error_bar.cancel_and_hide()
        self.clear_persistent_message()
        prompt = self.query_one("#command_prompt", CommandPrompt)
        prompt.show_prompt(callback, previous_focus_id, initial_text)

    def show_confirmation_prompt(
        self,
        message: str,
        callback: Callable[[bool], Awaitable[None]],
        previous_focus_id: str | None = None,
    ) -> None:
        """Display a confirmation prompt.

        Args:
            message: The confirmation message to display.
            callback: Function to call with True (yes) or False (no).
            previous_focus_id: Widget ID to return focus to on dismiss.
        """
        error_bar = self.query_one("#transient_error", TransientErrorBar)
        if error_bar.has_class("visible"):
            error_bar.cancel_and_hide()
        self.clear_persistent_message()
        prompt = self.query_one("#confirmation_prompt", ConfirmationPrompt)
        prompt.show_prompt(message, callback, previous_focus_id)

    def show_transient_error(self, message: str) -> None:
        """Display a transient error message.

        Args:
            message: The error message to display briefly.
        """
        self.clear_persistent_message()
        cmd_prompt = self.query_one("#command_prompt", CommandPrompt)
        confirm_prompt = self.query_one("#confirmation_prompt", ConfirmationPrompt)
        if cmd_prompt.has_class("visible") or confirm_prompt.has_class("visible"):
            return
        error_bar = self.query_one("#transient_error", TransientErrorBar)
        error_bar.show_error(message)

    def show_persistent_message(self, message: str) -> None:
        """Display a persistent message until dismissed.

        Args:
            message: The message to display.
        """
        error_bar = self.query_one("#transient_error", TransientErrorBar)
        if error_bar.has_class("visible"):
            error_bar.cancel_and_hide()
        persistent = self.query_one("#persistent_message", PersistentMessage)
        persistent.show_message(message)

    def clear_persistent_message(self) -> None:
        """Clear any visible persistent message."""
        persistent = self.query_one("#persistent_message", PersistentMessage)
        if persistent.has_class("visible"):
            persistent.clear_message()
