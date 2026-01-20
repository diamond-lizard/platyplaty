#!/usr/bin/env python3
"""Unit tests for autoplay continuation on playlist load."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.commands.load_play import handle_autoplay_continuation


class TestHandleAutoplayContinuation:
    """Tests for handle_autoplay_continuation function."""

    def test_no_autoplay_manager_does_nothing(self) -> None:
        """No action when autoplay_manager is None."""
        ctx = MagicMock()
        ctx.autoplay_manager = None
        handle_autoplay_continuation(ctx)
        # No exception raised

    def test_autoplay_disabled_does_not_restart_timer(self) -> None:
        """Timer not restarted when autoplay is disabled."""
        ctx = MagicMock()
        ctx.autoplay_manager.autoplay_enabled = False
        handle_autoplay_continuation(ctx)
        ctx.autoplay_manager._start_timer.assert_not_called()

    def test_autoplay_enabled_restarts_timer(self) -> None:
        """Timer restarted when autoplay is enabled."""
        ctx = MagicMock()
        ctx.autoplay_manager.autoplay_enabled = True
        handle_autoplay_continuation(ctx)
        ctx.autoplay_manager._start_timer.assert_called_once()
