#!/usr/bin/env python3
"""Tests for editing mode wiring into application.

These tests verify that the editing mode is properly wired into
AppContext and CommandPrompt, and that handle_command_key correctly
delegates to the editing mode.
"""

import sys
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
