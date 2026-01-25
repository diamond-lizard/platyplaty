#!/usr/bin/env python3
"""Unit tests for CommandLine persistent message integration.

Tests that CommandLine correctly manages PersistentMessage widget,
including show/clear methods and priority with other widgets.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.command_line import CommandLine
from platyplaty.ui.persistent_message import PersistentMessage


class TestCommandLineYieldsPersistentMessage:
    """Tests that CommandLine yields PersistentMessage."""

    def test_compose_yields_persistent_message(self) -> None:
        """CommandLine compose yields a PersistentMessage widget."""
        widget = CommandLine()
        children = list(widget.compose())
        types = [type(c) for c in children]
        assert PersistentMessage in types

    def test_persistent_message_has_correct_id(self) -> None:
        """PersistentMessage child has ID 'persistent_message'."""
        widget = CommandLine()
        children = list(widget.compose())
        msg = next(c for c in children if isinstance(c, PersistentMessage))
        assert msg.id == "persistent_message"
