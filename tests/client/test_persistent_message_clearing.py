#!/usr/bin/env python3
"""
Unit tests for persistent message clearing on keypress.

Tests that dispatch_focused_key_event clears any persistent message
before processing keys.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.keybinding_dispatch import dispatch_focused_key_event


@pytest.fixture
def mock_cmd_line() -> MagicMock:
    """Create a mock CommandLine widget."""
    cmd_line = MagicMock()
    cmd_line.clear_persistent_message = MagicMock()
    return cmd_line


@pytest.fixture
def mock_app(mock_cmd_line: MagicMock) -> MagicMock:
    """Create a mock PlatyplatyApp for testing dispatch."""
    app = MagicMock()
    app.run_action = AsyncMock()
    app.query_one = MagicMock(return_value=mock_cmd_line)
    return app


@pytest.fixture
def mock_ctx() -> MagicMock:
    """Create a mock AppContext with dispatch tables and focus."""
    ctx = MagicMock()
    ctx.exiting = False
    ctx.current_focus = "file_browser"
    ctx.global_dispatch_table = {"q": "quit"}
    ctx.file_browser_dispatch_table = {"j": "move_down", "k": "move_up"}
    ctx.playlist_dispatch_table = {}
    ctx.error_view_dispatch_table = {}
    return ctx


class TestPersistentMessageClearing:
    """Tests for persistent message clearing on keypress."""

    @pytest.mark.asyncio
    async def test_navigation_key_clears_persistent_message(
        self, mock_ctx: MagicMock, mock_app: MagicMock, mock_cmd_line: MagicMock
    ) -> None:
        """Navigation key clears persistent message and performs action."""
        result = await dispatch_focused_key_event("j", mock_ctx, mock_app)
        mock_cmd_line.clear_persistent_message.assert_called_once()
        assert result is True
        mock_app.run_action.assert_awaited_once_with("move_down")

    @pytest.mark.asyncio
    async def test_colon_key_clears_persistent_message(
        self, mock_ctx: MagicMock, mock_app: MagicMock, mock_cmd_line: MagicMock
    ) -> None:
        """Colon key clears persistent message before opening prompt."""
        # Note: colon opens command prompt, which is handled specially
        result = await dispatch_focused_key_event("colon", mock_ctx, mock_app)
        mock_cmd_line.clear_persistent_message.assert_called_once()
        assert result is True

    @pytest.mark.asyncio
    async def test_unbound_key_clears_persistent_message(
        self, mock_ctx: MagicMock, mock_app: MagicMock, mock_cmd_line: MagicMock
    ) -> None:
        """Unbound key still clears persistent message."""
        result = await dispatch_focused_key_event("z", mock_ctx, mock_app)
        mock_cmd_line.clear_persistent_message.assert_called_once()
        assert result is False
        mock_app.run_action.assert_not_called()

    @pytest.mark.asyncio
    async def test_clearing_no_persistent_message_is_safe(
        self, mock_ctx: MagicMock, mock_app: MagicMock, mock_cmd_line: MagicMock
    ) -> None:
        """Clearing when no message is showing does not cause errors."""
        # The clear_persistent_message should be a no-op when nothing visible
        result = await dispatch_focused_key_event("q", mock_ctx, mock_app)
        mock_cmd_line.clear_persistent_message.assert_called_once()
        assert result is True
